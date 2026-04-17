"""
FEMA public APIs for flood zone and hazard risk data.
  - NFHL (National Flood Hazard Layer): flood zone designation by lat/lon
  - NRI  (National Risk Index): composite hazard risk rating by census tract
"""
from typing import Any

import httpx

from app.utils.logging import LatencyTracker, get_logger

logger = get_logger(__name__)

_NFHL_URL = "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query"
_NRI_URL = "https://services.arcgis.com/XG15cJAlne2vxtgt/arcgis/rest/services/National_Risk_Index_Census_Tracts/FeatureServer/0/query"
_TIMEOUT = 10.0


async def get_flood_zone(
    client: httpx.AsyncClient, lat: float, lon: float
) -> str | None:
    """
    Query FEMA NFHL for the flood zone designation at a lat/lon point.
    Returns the zone string (e.g. 'AE', 'X') or None if not found.
    """
    params = {
        "geometry": f"{lon},{lat}",
        "geometryType": "esriGeometryPoint",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "FLD_ZONE",
        "returnGeometry": "false",
        "f": "json",
    }
    with LatencyTracker(logger, "FEMA", "flood_zone"):
        resp = await client.get(_NFHL_URL, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()

    features = data.get("features", [])
    if not features:
        return None
    return features[0].get("attributes", {}).get("FLD_ZONE")


async def get_hazard_risk(
    client: httpx.AsyncClient, state_fips: str, county_fips: str, tract: str
) -> str | None:
    """
    Query FEMA National Risk Index for the composite hazard risk rating
    of a census tract. Returns a rating string such as 'Very High',
    'Relatively High', 'Relatively Moderate', 'Relatively Low', 'Very Low',
    or None if unavailable.

    tract should be the raw ATTOM tract (e.g. '9702'); this function
    builds the full 11-digit tract FIPS internally.
    """
    # Build full 11-digit census tract FIPS: state(2) + county(3) + tract(6)
    tract_padded = tract.zfill(6) if len(tract) < 6 else tract
    county_padded = county_fips.zfill(3)
    tract_fips = f"{state_fips}{county_padded}{tract_padded}"

    params = {
        "where": f"TRACTFIPS='{tract_fips}'",
        "outFields": "RISK_RATNG",
        "returnGeometry": "false",
        "f": "json",
    }
    with LatencyTracker(logger, "FEMA", "hazard_risk"):
        resp = await client.get(_NRI_URL, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()

    features = data.get("features", [])
    logger.info("RAW NRI response", extra={"extra": {"data": str(data)[:500]}})
    if not features:
        return None
    return features[0].get("attributes", {}).get("RISK_RATNG") or None
