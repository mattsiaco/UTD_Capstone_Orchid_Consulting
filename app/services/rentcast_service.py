"""
RentCast API client.
Used to retrieve days on market for a given address.
"""
import os
from typing import Any

import httpx

from app.utils.logging import LatencyTracker, get_logger

logger = get_logger(__name__)

_BASE_URL = "https://api.rentcast.io/v1"
_TIMEOUT = 10.0


def _api_key() -> str:
    key = os.getenv("RENTCAST_API_KEY", "")
    if not key:
        raise RuntimeError("RENTCAST_API_KEY environment variable is not set")
    return key


def _headers() -> dict[str, str]:
    return {
        "Accept": "application/json",
        "X-Api-Key": _api_key(),
    }


async def get_listing_stats(
    client: httpx.AsyncClient, address: str, zip_code: str
) -> dict[str, Any]:
    """
    Fetch market statistics for a zip code from RentCast.
    Returns the raw response dict.
    """
    with LatencyTracker(logger, "RentCast", "listing_stats"):
        resp = await client.get(
            f"{_BASE_URL}/markets",
            headers=_headers(),
            params={"zipCode": zip_code},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()


def parse_days_on_market(data: dict[str, Any]) -> int | None:
    """Extract average days on market from a RentCast markets response."""
    logger.info("RAW RentCast response", extra={"extra": {"data": str(data)[:600]}})
    try:
        val = (
            data.get("averageDaysOnMarket")
            or data.get("daysOnMarket")
            or data.get("saleData", {}).get("averageDaysOnMarket")
            or data.get("saleData", {}).get("daysOnMarket")
        )
        if val is None:
            return None
        return int(round(float(val)))
    except (TypeError, ValueError):
        return None
