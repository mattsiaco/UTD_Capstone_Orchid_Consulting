"""
ATTOM Data Solutions API client.

All public methods raise httpx.HTTPStatusError on non-2xx responses
and httpx.TimeoutException on timeouts. The enrichment_service handles
retries and fallback logic.
"""
import os
from typing import Any

import httpx

from app.utils.logging import LatencyTracker, get_logger

logger = get_logger(__name__)

_BASE_URL = "https://api.gateway.attomdata.com"
_TIMEOUT = 10.0  # seconds per request
_HEADERS_TEMPLATE = {
    "Accept": "application/json",
    "apikey": "",  # filled per-request from env
}


def _api_key() -> str:
    key = os.getenv("ATTOM_API_KEY", "")
    if not key:
        raise RuntimeError("ATTOM_API_KEY environment variable is not set")
    return key


def _headers() -> dict[str, str]:
    return {**_HEADERS_TEMPLATE, "apikey": _api_key()}


def _split_address(address: str) -> tuple[str, str]:
    """
    Split 'street, city, state zip' into (address1, address2).
    address1 = street portion, address2 = everything after first comma.
    """
    parts = address.split(",", 1)
    address1 = parts[0].strip()
    address2 = parts[1].strip() if len(parts) > 1 else ""
    return address1, address2


async def lookup_address(client: httpx.AsyncClient, address: str) -> dict[str, Any]:
    """Normalize address and return ATTOM property identifier + lat/lon."""
    address1, address2 = _split_address(address)
    with LatencyTracker(logger, "ATTOM", "lookup_address"):
        resp = await client.get(
            f"{_BASE_URL}/propertyapi/v1.0.0/property/address",
            headers=_headers(),
            params={"address1": address1, "address2": address2},
            timeout=_TIMEOUT,
        )
        logger.info(
            "ATTOM lookup_address response",
            extra={"extra": {"status": resp.status_code, "body_preview": resp.text[:300]}},
        )
        resp.raise_for_status()
        if not resp.text.strip():
            raise ValueError("ATTOM lookup_address returned empty body")
        return resp.json()


async def get_property_detail(
    client: httpx.AsyncClient, attom_id: str
) -> dict[str, Any]:
    """Fetch expanded property profile by ATTOM ID."""
    with LatencyTracker(logger, "ATTOM", "property_detail"):
        resp = await client.get(
            f"{_BASE_URL}/propertyapi/v1.0.0/property/expandedprofile",
            headers=_headers(),
            params={"attomid": attom_id},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()


async def get_neighborhood(
    client: httpx.AsyncClient, attom_id: str
) -> dict[str, Any]:
    """Fetch neighborhood/community data via the detail-with-schools profile."""
    with LatencyTracker(logger, "ATTOM", "neighborhood"):
        resp = await client.get(
            f"{_BASE_URL}/propertyapi/v1.0.0/property/detailwithschools",
            headers=_headers(),
            params={"attomid": attom_id},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()


async def get_market(client: httpx.AsyncClient, zip_code: str) -> dict[str, Any]:
    """Fetch market trends and sales data for a zip code."""
    with LatencyTracker(logger, "ATTOM", "market"):
        resp = await client.get(
            f"{_BASE_URL}/propertyapi/v1.0.0/sale/snapshot",
            headers=_headers(),
            params={"postalcode": zip_code},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()


async def get_rental_avm(
    client: httpx.AsyncClient, attom_id: str
) -> dict[str, Any]:
    """Fetch AVM estimate (rental value derived from AVM detail)."""
    with LatencyTracker(logger, "ATTOM", "rental_avm"):
        resp = await client.get(
            f"{_BASE_URL}/propertyapi/v1.0.0/avm/detail",
            headers=_headers(),
            params={"attomid": attom_id},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()


async def get_climate_risk(
    client: httpx.AsyncClient, attom_id: str
) -> dict[str, Any]:
    """Fetch climate and flood hazard data."""
    with LatencyTracker(logger, "ATTOM", "climate_risk"):
        resp = await client.get(
            f"{_BASE_URL}/propertyapi/v1.0.0/property/basicprofile",
            headers=_headers(),
            params={"attomid": attom_id},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
