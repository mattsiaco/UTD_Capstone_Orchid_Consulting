"""Unit tests for Census data parsers (no network calls)."""
from app.services.census_service import (
    parse_homeownership_rate,
    parse_median_income,
    parse_unemployment_rate,
)


CENSUS_ROW = {
    "B19013_001E": "85000",
    "B25003_001E": "1000",
    "B25003_002E": "650",
    "B23025_002E": "5000",
    "B23025_005E": "200",
    "B01003_001E": "12000",
}


def test_median_income():
    assert parse_median_income(CENSUS_ROW) == 85000.0


def test_median_income_negative_sentinel():
    assert parse_median_income({"B19013_001E": "-666666666"}) is None


def test_homeownership_rate():
    assert parse_homeownership_rate(CENSUS_ROW) == 65.0


def test_unemployment_rate():
    assert parse_unemployment_rate(CENSUS_ROW) == 4.0


def test_missing_keys():
    assert parse_median_income({}) is None
    assert parse_homeownership_rate({}) is None
    assert parse_unemployment_rate({}) is None
