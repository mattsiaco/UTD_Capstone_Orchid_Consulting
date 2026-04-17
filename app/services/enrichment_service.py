"""
Orchestrates all external API calls, applies fallback logic,
and assembles the final enriched property response dict.
"""
import asyncio
import json
from typing import Any

import httpx

from app.mappers import attom_mapper
from app.services import attom_service, census_service, fema_service, geocoding_service, rentcast_service, zoning_service
from app.utils.logging import get_logger

logger = get_logger(__name__)

_MAX_RETRIES = 3
_RETRY_STATUSES = {429, 500, 502, 503, 504}


async def _with_retry(coro_fn, *args, **kwargs) -> dict[str, Any] | None:
    """
    Call an async function up to _MAX_RETRIES times.
    Returns None on final failure instead of raising.
    """
    last_exc: Exception | None = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            return await coro_fn(*args, **kwargs)
        except httpx.HTTPStatusError as exc:
            last_exc = exc
            logger.error(
                "HTTP error from provider",
                extra={"extra": {"status": exc.response.status_code, "body": exc.response.text[:500]}},
            )
            if exc.response.status_code not in _RETRY_STATUSES:
                break
            wait = 2 ** (attempt - 1)
            logger.warning(
                "retryable HTTP error",
                extra={
                    "extra": {
                        "attempt": attempt,
                        "status": exc.response.status_code,
                        "wait_sec": wait,
                    }
                },
            )
            if attempt < _MAX_RETRIES:
                await asyncio.sleep(wait)
        except (httpx.TimeoutException, httpx.RequestError) as exc:
            last_exc = exc
            wait = 2 ** (attempt - 1)
            logger.warning(
                "request error",
                extra={"extra": {"attempt": attempt, "error": str(exc), "wait_sec": wait}},
            )
            if attempt < _MAX_RETRIES:
                await asyncio.sleep(wait)
        except json.JSONDecodeError as exc:
            last_exc = exc
            logger.error("provider returned empty/invalid JSON body", extra={"extra": {"error": str(exc)}})
            break

    logger.error(
        "all retries exhausted",
        extra={"extra": {"error": str(last_exc)}},
    )
    return None


async def enrich(address: str) -> dict[str, Any]:
    """
    Full enrichment pipeline for a U.S. address.
    Returns the raw dict that will be validated by Pydantic in the route layer.
    Raises ValueError with a user-facing message if ATTOM address lookup fails.
    """
    async with httpx.AsyncClient() as client:
        # Step 1 — normalize address via ATTOM
        address_resp = await _with_retry(attom_service.lookup_address, client, address)
        if not address_resp:
            raise ValueError("Address not found via ATTOM")

        attom_id = attom_mapper.extract_attom_id(address_resp)
        if not attom_id:
            raise ValueError("Could not resolve ATTOM property ID for this address")

        lat, lon = attom_mapper.extract_lat_lon(address_resp)
        zip_code = attom_mapper.extract_zip(address_resp)
        state_fips, county_fips = attom_mapper.extract_fips(address_resp)
        # tract comes from expandedprofile (richer area data); resolved after detail call below
        tract: str | None = None

        # ATTOM calls — parallel, handles all property fields + school ratings + market sales
        detail_task = asyncio.create_task(
            _with_retry(attom_service.get_property_detail, client, attom_id)
        )
        nbhd_task = asyncio.create_task(
            _with_retry(attom_service.get_neighborhood, client, attom_id)
        )
        market_task = asyncio.create_task(
            _with_retry(attom_service.get_market, client, zip_code or "")
        )
        rental_task = asyncio.create_task(
            _with_retry(attom_service.get_rental_avm, client, attom_id)
        )
        climate_task = asyncio.create_task(
            _with_retry(attom_service.get_climate_risk, client, attom_id)
        )

        detail_resp, nbhd_resp, market_resp, rental_resp, climate_resp = (
            await asyncio.gather(
                detail_task, nbhd_task, market_task, rental_task, climate_task
            )
        )

        # Resolve census tract from detail response (has richer area data than address lookup)
        if detail_resp:
            tract = attom_mapper.extract_census_tract(detail_resp)

        logger.info(
            "Census identifiers",
            extra={"extra": {"state_fips": state_fips, "county_fips": county_fips, "tract": tract}},
        )
        if detail_resp and detail_resp.get("property"):
            area = detail_resp["property"][0].get("area", {})
            logger.info("RAW area block", extra={"extra": {"area": json.dumps(area)[:400]}})

        # Debug: log specific sub-structures needed for mapping
        if market_resp and market_resp.get("property"):
            sale = market_resp["property"][0].get("sale", {})
            logger.info("RAW market sale structure", extra={"extra": {"sale": json.dumps(sale)[:400]}})
        if nbhd_resp and nbhd_resp.get("property"):
            schools = nbhd_resp["property"][0].get("school", [])
            logger.info("RAW school structure", extra={"extra": {"school_sample": json.dumps(schools[:2] if isinstance(schools, list) else schools)[:400]}})
        if detail_resp and detail_resp.get("property"):
            rooms = detail_resp["property"][0].get("building", {}).get("rooms", {})
            logger.info("RAW building.rooms", extra={"extra": {"rooms": json.dumps(rooms)}})

        # Map ATTOM responses — property, school ratings, market sales/AVM
        property_data = attom_mapper.map_property(
            detail_resp or {}, climate_resp or {}
        )
        neighborhood_data = attom_mapper.map_neighborhood(nbhd_resp or {})
        market_data = attom_mapper.map_market(market_resp or {}, rental_resp or {})

        # Step 1 of zoning pipeline — geocode if ATTOM didn't return coordinates
        if lat is None or lon is None:
            lat, lon = await _with_retry(geocoding_service.geocode, client, address)

        # FEMA + RentCast + zoning ArcGIS — all run in parallel
        fema_flood_task = (
            asyncio.create_task(_with_retry(fema_service.get_flood_zone, client, lat, lon))
            if lat is not None and lon is not None
            else None
        )
        fema_risk_task = (
            asyncio.create_task(
                _with_retry(fema_service.get_hazard_risk, client, state_fips, county_fips, tract)
            )
            if state_fips and county_fips and tract
            else None
        )
        rentcast_task = (
            asyncio.create_task(
                _with_retry(rentcast_service.get_listing_stats, client, address, zip_code)
            )
            if zip_code
            else None
        )
        zoning_task = (
            asyncio.create_task(zoning_service.get_county_zoning(client, lat, lon))
            if lat is not None and lon is not None
            else None
        )

        fema_zone = await fema_flood_task if fema_flood_task else None
        fema_risk = await fema_risk_task if fema_risk_task else None
        rentcast_resp = await rentcast_task if rentcast_task else None
        arcgis_zoning = await zoning_task if zoning_task else None

        if fema_zone:
            property_data["floodZone"] = fema_zone
        if fema_risk:
            property_data["hazardRiskZone"] = fema_risk
        if rentcast_resp:
            dom = rentcast_service.parse_days_on_market(rentcast_resp)
            if dom is not None:
                market_data["daysOnMarket"] = dom

        # Zoning fallback chain: county ArcGIS → ATTOM field → "Unknown"
        attom_zoning = market_data.get("zoningInformation")
        market_data["zoningInformation"] = zoning_service.resolve(arcgis_zoning, attom_zoning)

        # Census — always used for demographics + market value/growth (not a fallback)
        if state_fips and county_fips and tract:
            census_task = asyncio.create_task(
                _with_retry(census_service.get_demographics, client, state_fips, county_fips, tract)
            )
            older_pop_task = asyncio.create_task(
                _with_retry(census_service.get_population_older, client, state_fips, county_fips, tract)
            )
            census_data, older_data = await asyncio.gather(census_task, older_pop_task)

            if census_data:
                logger.info("Census demographics fetched")
                neighborhood_data["medianHouseholdIncome"] = census_service.parse_median_income(census_data)
                neighborhood_data["homeownershipRate"] = census_service.parse_homeownership_rate(census_data)
                neighborhood_data["unemploymentRate"] = census_service.parse_unemployment_rate(census_data)
                market_data["medianHomeValue"] = census_service.parse_median_home_value(census_data)

            if census_data and older_data:
                logger.info("Census population growth fetched")
                market_data["populationGrowth"] = census_service.parse_population_growth(census_data, older_data)
        else:
            logger.warning("Census skipped — missing state_fips, county_fips, or tract")

        _log_completeness(property_data, neighborhood_data, market_data)

        return {
            "property": property_data,
            "neighborhood": neighborhood_data,
            "market": market_data,
        }


def _log_completeness(
    prop: dict, nbhd: dict, mkt: dict
) -> None:
    def pct(d: dict) -> float:
        filled = sum(1 for v in d.values() if v is not None)
        return round(filled / len(d) * 100, 1) if d else 0.0

    logger.info(
        "field completeness",
        extra={
            "extra": {
                "property_pct": pct(prop),
                "neighborhood_pct": pct(nbhd),
                "market_pct": pct(mkt),
            }
        },
    )
