"""
Zoning information lookup.

Pipeline:
  1. Spatial point query against the county's ArcGIS zoning layer
     (via the ESRI national zoning dataset on ArcGIS Online)
  2. ATTOM zoning field (passed in from the caller)
  3. "Unknown"

All results are passed through humanize() before being returned.
"""
from typing import Any

import httpx

from app.utils.logging import LatencyTracker, get_logger

logger = get_logger(__name__)

# Ordered list of ArcGIS zoning endpoints to try. Each entry is a dict with:
#   url      — ArcGIS feature layer query URL
#   fields   — outFields to request
# Tried in order; first non-empty result wins.
_ZONING_SOURCES: list[dict] = [
    {
        # City of Dallas base zoning layer (primary)
        "url": "https://gis.dallascityhall.com/wwwgis/rest/services/Sdc_public/Zoning/MapServer/0/query",
        "fields": "ZONE_DIST,ZONE_DESC",
    },
    {
        # City of Dallas base zoning layer (alternate host)
        "url": "https://egis.dallascityhall.com/arcgis/rest/services/Sdc_public/Zoning/MapServer/0/query",
        "fields": "ZONE_DIST,ZONE_DESC",
    },
    {
        # ESRI national parcel dataset (broad but incomplete coverage)
        "url": (
            "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/"
            "USA_Parcels/FeatureServer/0/query"
        ),
        "fields": "ZONING,ZONING_TYPE,ZONE_CODE,ZONE_DESCRIPTION,ZONE_TYPE",
    },
]
_TIMEOUT = 10.0

# Human-readable labels for the most common US zoning prefix codes.
# Matched by prefix so "R-1A", "R1", "RA" etc. all resolve.
_PREFIX_LABELS: list[tuple[str, str]] = [
    ("AG",  "Agricultural"),
    ("A",   "Agricultural"),
    ("RR",  "Rural Residential"),
    ("RE",  "Residential Estate"),
    ("RS",  "Single-Family Residential"),
    ("RSF", "Single-Family Residential"),
    ("SF",  "Single-Family Residential"),
    ("R",   "Residential"),
    ("MF",  "Multi-Family Residential"),
    ("MH",  "Mobile Home / Manufactured Housing"),
    ("PD",  "Planned Development"),
    ("PUD", "Planned Unit Development"),
    ("MX",  "Mixed Use"),
    ("MU",  "Mixed Use"),
    ("NC",  "Neighborhood Commercial"),
    ("LC",  "Local Commercial"),
    ("GC",  "General Commercial"),
    ("CB",  "Central Business"),
    ("CBD", "Central Business District"),
    ("C",   "Commercial"),
    ("O",   "Office"),
    ("OP",  "Office / Professional"),
    ("LI",  "Light Industrial"),
    ("HI",  "Heavy Industrial"),
    ("I",   "Industrial"),
    ("P",   "Public / Institutional"),
    ("PI",  "Public / Institutional"),
    ("OS",  "Open Space"),
    ("PR",  "Parks and Recreation"),
    ("F",   "Floodplain"),
    ("FP",  "Floodplain"),
]


def humanize(code: str | None) -> str | None:
    """
    Convert a raw zoning code (e.g. 'SF-1', 'R-2', 'C-2') into a
    human-readable label. Returns None if code is None or empty.
    """
    if not code:
        return None
    code = code.strip()
    if not code:
        return None

    upper = code.upper()
    for prefix, label in _PREFIX_LABELS:
        if upper == prefix or upper.startswith(prefix + "-") or upper.startswith(prefix + " "):
            suffix = upper[len(prefix):].lstrip("- ")
            return f"{label} ({code})" if suffix else label

    # No prefix matched — return the raw code so it's at least visible
    return code


async def get_county_zoning(
    client: httpx.AsyncClient, lat: float, lon: float
) -> str | None:
    """
    Try each ArcGIS zoning source in order until one returns features.
    Returns a humanized zoning string or None if all sources fail.
    """
    base_params = {
        "geometry": f"{lon},{lat}",
        "geometryType": "esriGeometryPoint",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "returnGeometry": "false",
        "f": "json",
    }

    for source in _ZONING_SOURCES:
        try:
            params = {**base_params, "outFields": source["fields"]}
            with LatencyTracker(logger, "Zoning", "county_arcgis"):
                resp = await client.get(source["url"], params=params, timeout=_TIMEOUT)
                resp.raise_for_status()
                data: dict[str, Any] = resp.json()

            features = data.get("features", [])
            if not features:
                logger.info("Zoning source returned no features", extra={"extra": {"url": source["url"]}})
                continue

            attrs = features[0].get("attributes", {})
            logger.info("RAW zoning attributes", extra={"extra": {"source": source["url"], "attrs": str(attrs)}})

            description = attrs.get("ZONE_DESC") or attrs.get("ZONE_DESCRIPTION") or ""
            code = (
                attrs.get("ZONE_DIST")
                or attrs.get("ZONE_CODE")
                or attrs.get("ZONING")
                or attrs.get("ZONING_TYPE")
                or attrs.get("ZONE_TYPE")
                or attrs.get("ZoningClass")
                or ""
            )

            if description and description.strip():
                return description.strip().title()
            if code:
                return humanize(code)

        except Exception as exc:
            logger.warning("Zoning source failed", extra={"extra": {"url": source["url"], "error": str(exc)}})
            continue

    logger.info("All zoning sources exhausted — no data found")
    return None


def resolve(arcgis_result: str | None, attom_zoning: str | None) -> str:
    """
    Apply the fallback chain and always return a string.
      1. County ArcGIS result
      2. ATTOM zoning field
      3. "Unknown"
    """
    if arcgis_result:
        return arcgis_result
    if attom_zoning and attom_zoning.strip():
        return humanize(attom_zoning) or "Unknown"
    return "Unknown"
