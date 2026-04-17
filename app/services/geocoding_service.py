"""
Google Maps Geocoding API.
Used to obtain lat/lon when ATTOM does not return coordinates.
"""
import os
from typing import Any

import httpx

from app.utils.logging import LatencyTracker, get_logger

logger = get_logger(__name__)

_BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
_TIMEOUT = 10.0


def _api_key() -> str:
    key = os.getenv("GEOCODING_API_KEY", "")
    if not key:
        raise RuntimeError("GEOCODING_API_KEY environment variable is not set")
    return key


async def geocode(
    client: httpx.AsyncClient, address: str
) -> tuple[float | None, float | None]:
    """
    Geocode a free-text address.
    Returns (lat, lon) or (None, None) if geocoding fails.
    """
    with LatencyTracker(logger, "Geocoding", "geocode"):
        resp = await client.get(
            _BASE_URL,
            params={"address": address, "key": _api_key()},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()

    results = data.get("results", [])
    if not results:
        logger.warning("Geocoding returned no results", extra={"extra": {"address": address}})
        return None, None

    loc = results[0]["geometry"]["location"]
    return loc["lat"], loc["lng"]
