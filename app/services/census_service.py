"""
U.S. Census Bureau American Community Survey (ACS) 5-Year Estimates API.
Used as fallback for neighborhood demographics and market population growth.

Variables used:
  B19013_001E  — median household income
  B25003_001E  — total occupied housing units (denominator for homeownership rate)
  B25003_002E  — owner-occupied housing units (numerator for homeownership rate)
  B23025_005E  — unemployed (civilian labor force)
  B23025_002E  — civilian labor force (denominator for unemployment rate)
  B01003_001E  — total population (used across years to estimate growth)
  B25077_001E  — median home value
"""
import os
from typing import Any

import httpx

from app.utils.logging import LatencyTracker, get_logger

logger = get_logger(__name__)

_BASE_URL_2022 = "https://api.census.gov/data/2022/acs/acs5"
_BASE_URL_2018 = "https://api.census.gov/data/2018/acs/acs5"
_TIMEOUT = 10.0


def _api_key() -> str:
    return os.getenv("CENSUS_API_KEY", "")  # key is optional for low-volume use


def _pad_tract(tract: str) -> str:
    """Census API requires 6-digit zero-padded tract (e.g. '9702' → '970200')."""
    return tract.zfill(6) if len(tract) < 6 else tract


async def get_demographics(
    client: httpx.AsyncClient, state_fips: str, county_fips: str, tract: str
) -> dict[str, Any]:
    """
    Fetch ACS demographics for a census tract.
    state_fips, county_fips, and tract must be zero-padded FIPS strings.
    """
    variables = ",".join([
        "B19013_001E",
        "B25003_001E",
        "B25003_002E",
        "B23025_005E",
        "B23025_002E",
        "B01003_001E",
        "B25077_001E",
    ])
    params: dict[str, str] = {
        "get": variables,
        "for": f"tract:{_pad_tract(tract)}",
        "in": f"state:{state_fips} county:{county_fips}",
    }
    if key := _api_key():
        params["key"] = key

    with LatencyTracker(logger, "Census", "demographics"):
        resp = await client.get(_BASE_URL_2022, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        rows = resp.json()

    if len(rows) < 2:
        return {}

    headers, values = rows[0], rows[1]
    return dict(zip(headers, values))


async def get_population_older(
    client: httpx.AsyncClient, state_fips: str, county_fips: str, tract: str
) -> dict[str, Any]:
    """
    Fetch 2018 ACS population for the same tract to compute 4-year growth vs 2022.
    """
    params: dict[str, str] = {
        "get": "B01003_001E",
        "for": f"tract:{_pad_tract(tract)}",
        "in": f"state:{state_fips} county:{county_fips}",
    }
    if key := _api_key():
        params["key"] = key

    with LatencyTracker(logger, "Census", "population_2018"):
        resp = await client.get(_BASE_URL_2018, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        rows = resp.json()

    if len(rows) < 2:
        return {}

    headers, values = rows[0], rows[1]
    return dict(zip(headers, values))


def parse_median_income(data: dict[str, Any]) -> float | None:
    raw = data.get("B19013_001E")
    try:
        val = float(raw)
        return val if val >= 0 else None
    except (TypeError, ValueError):
        return None


def parse_homeownership_rate(data: dict[str, Any]) -> float | None:
    try:
        total = float(data["B25003_001E"])
        owner = float(data["B25003_002E"])
        if total <= 0:
            return None
        return round(owner / total * 100, 2)
    except (TypeError, ValueError, KeyError):
        return None


def parse_unemployment_rate(data: dict[str, Any]) -> float | None:
    try:
        labor_force = float(data["B23025_002E"])
        unemployed = float(data["B23025_005E"])
        if labor_force <= 0:
            return None
        return round(unemployed / labor_force * 100, 2)
    except (TypeError, ValueError, KeyError):
        return None


def parse_median_home_value(data: dict[str, Any]) -> float | None:
    raw = data.get("B25077_001E")
    try:
        val = float(raw)
        return val if val >= 0 else None
    except (TypeError, ValueError):
        return None


def parse_population_growth(
    current_data: dict[str, Any], older_data: dict[str, Any]
) -> float | None:
    """Returns 4-year population growth rate (2018→2022) as a percentage."""
    try:
        pop_2022 = float(current_data["B01003_001E"])
        pop_2018 = float(older_data["B01003_001E"])
        if pop_2018 <= 0:
            return None
        return round((pop_2022 - pop_2018) / pop_2018 * 100, 2)
    except (TypeError, ValueError, KeyError):
        return None
