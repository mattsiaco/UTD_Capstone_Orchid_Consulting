"""
Maps raw ATTOM API payloads into the internal property schema dicts.
All helpers return None rather than raising when a field is absent.
"""
from typing import Any


def _safe_float(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Address lookup → identifiers
# ---------------------------------------------------------------------------

def extract_attom_id(address_resp: dict[str, Any]) -> str | None:
    try:
        return str(
            address_resp["property"][0]["identifier"]["attomId"]
        )
    except (KeyError, IndexError, TypeError):
        return None


def extract_lat_lon(address_resp: dict[str, Any]) -> tuple[float | None, float | None]:
    try:
        loc = address_resp["property"][0]["location"]
        return _safe_float(loc.get("latitude")), _safe_float(loc.get("longitude"))
    except (KeyError, IndexError, TypeError):
        return None, None


def extract_zip(address_resp: dict[str, Any]) -> str | None:
    try:
        return address_resp["property"][0]["address"].get("postal1")
    except (KeyError, IndexError, TypeError):
        return None


def extract_fips(address_resp: dict[str, Any]) -> tuple[str | None, str | None]:
    """
    Returns (state_fips, county_fips) from identifier.fips (e.g. '48113' → '48', '113').
    Census tract is extracted separately from the detail response via extract_census_tract.
    """
    try:
        fips_str = str(address_resp["property"][0]["identifier"].get("fips", ""))
        if len(fips_str) >= 5:
            return fips_str[:2], fips_str[2:]
        return None, None
    except (KeyError, IndexError, TypeError):
        return None, None


def extract_census_tract(detail_resp: dict[str, Any]) -> str | None:
    """Extract census tract from the expanded profile response."""
    try:
        return detail_resp["property"][0]["area"].get("censusTractIdent")
    except (KeyError, IndexError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Property
# ---------------------------------------------------------------------------

def map_property(detail_resp: dict[str, Any], climate_resp: dict[str, Any]) -> dict[str, Any]:
    prop: dict[str, Any] = {
        "yearBuilt": None,
        "constructionType": None,
        "squareFootage": None,
        "numBedrooms": None,
        "numBathrooms": None,
        "numFloors": None,
        "roofType": None,
        "foundationType": None,
        "floodZone": None,
        "hazardRiskZone": None,
    }
    try:
        summary = detail_resp["property"][0]["summary"]
        prop["yearBuilt"] = _safe_int(summary.get("yearBuilt"))
        prop["constructionType"] = summary.get("propClass")
    except (KeyError, IndexError, TypeError):
        pass

    try:
        building = detail_resp["property"][0]["building"]
        size = building.get("size", {})
        prop["squareFootage"] = _safe_float(size.get("livingSize") or size.get("universalsize") or size.get("bldgSize"))
        rooms = building.get("rooms", {})
        prop["numBedrooms"] = _safe_float(rooms.get("beds"))
        # ATTOM uses both casing variants depending on endpoint
        prop["numBathrooms"] = _safe_float(
            rooms.get("bathsTotal") or rooms.get("bathstotal") or rooms.get("bathsFull")
        )
        prop["numFloors"] = _safe_int(
            building.get("storiesTotal")
            or building.get("stories")
            or building.get("summary", {}).get("stories")
        )
        construction = building.get("construction", {})
        prop["roofType"] = construction.get("roofCover") or construction.get("roofcover")
        prop["foundationType"] = (
            construction.get("foundationType") or construction.get("foundationtype")
        )
    except (KeyError, IndexError, TypeError):
        pass

    # floodZone/hazardRiskZone not available from basicprofile — filled by FEMA fallback
    return prop


# ---------------------------------------------------------------------------
# Neighborhood
# ---------------------------------------------------------------------------

def map_neighborhood(neighborhood_resp: dict[str, Any]) -> dict[str, Any]:
    nbhd: dict[str, Any] = {
        "medianHouseholdIncome": None,
        "unemploymentRate": None,
        "schoolRatings": None,
        "crimeStatistics": None,
        "homeownershipRate": None,
    }
    # Extract school rating — schoolRating is a letter grade (e.g. "C-"), GSTestRating is numeric
    _letter_to_gpa = {
        "A+": 4.3, "A": 4.0, "A-": 3.7,
        "B+": 3.3, "B": 3.0, "B-": 2.7,
        "C+": 2.3, "C": 2.0, "C-": 1.7,
        "D+": 1.3, "D": 1.0, "D-": 0.7,
        "F": 0.0,
    }
    try:
        school_data = neighborhood_resp["property"][0].get("school", [])
        if isinstance(school_data, list) and school_data:
            ratings: list[float] = []
            for s in school_data:
                if not isinstance(s, dict):
                    continue
                gs = _safe_float(s.get("GSTestRating"))
                if gs is not None and gs > 0:
                    ratings.append(gs)
                    continue
                letter = str(s.get("schoolRating", "")).strip()
                gpa = _letter_to_gpa.get(letter)
                if gpa is not None:
                    ratings.append(gpa)
            if ratings:
                nbhd["schoolRatings"] = round(sum(ratings) / len(ratings), 2)
    except (KeyError, IndexError, TypeError):
        pass

    return nbhd


# ---------------------------------------------------------------------------
# Market
# ---------------------------------------------------------------------------

def map_market(
    market_resp: dict[str, Any],
    rental_resp: dict[str, Any],
) -> dict[str, Any]:
    mkt: dict[str, Any] = {
        "populationGrowth": None,
        "medianHomeValue": None,
        "homePriceAppreciationRate": None,
        "daysOnMarket": None,
        "rentPrices": None,
        "zoningInformation": None,
    }
    # sale/snapshot returns a list of recent sales; derive median and avg DOM
    try:
        sales = market_resp["property"]
        sale_amts = [
            _safe_float(p.get("sale", {}).get("amount", {}).get("saleAmt"))
            for p in sales
        ]
        sale_amts = sorted(a for a in sale_amts if a)
        if sale_amts:
            mid = len(sale_amts) // 2
            mkt["medianHomeValue"] = sale_amts[mid]

        doms = [
            _safe_int(p.get("sale", {}).get("calculation", {}).get("dom"))
            for p in sales
        ]
        doms = [d for d in doms if d is not None]
        if doms:
            mkt["daysOnMarket"] = round(sum(doms) / len(doms))

        price_per_sf = [
            _safe_float(
                p.get("sale", {}).get("calculation", {}).get("pricPerSizeUnit")
                or p.get("sale", {}).get("calculation", {}).get("pricepersizeunit")
            )
            for p in sales
        ]
        price_per_sf = [v for v in price_per_sf if v]
        if price_per_sf:
            mkt["homePriceAppreciationRate"] = round(sum(price_per_sf) / len(price_per_sf), 2)

        zoning = next(
            (p.get("lot", {}).get("zoningType") for p in sales if p.get("lot", {}).get("zoningType")),
            None,
        )
        mkt["zoningInformation"] = zoning
    except (KeyError, IndexError, TypeError):
        pass

    # AVM detail → estimated home value (used as rentPrices proxy until rental AVM available)
    try:
        avm = rental_resp["property"][0]["avm"]
        mkt["rentPrices"] = _safe_float(avm.get("amount", {}).get("value"))
    except (KeyError, IndexError, TypeError):
        pass

    return mkt
