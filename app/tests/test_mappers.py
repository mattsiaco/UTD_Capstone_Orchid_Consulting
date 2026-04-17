"""Unit tests for attom_mapper field extraction."""
import pytest
from app.mappers import attom_mapper


ADDRESS_RESP = {
    "property": [
        {
            "identifier": {"attomId": "12345678"},
            "location": {"latitude": "32.7767", "longitude": "-96.7970"},
            "address": {"postal1": "75201"},
            "area": {
                "countrySecSubd": "48",
                "countyFips": "113",
                "censusBlockGroup": "001234",
            },
        }
    ]
}


def test_extract_attom_id():
    assert attom_mapper.extract_attom_id(ADDRESS_RESP) == "12345678"


def test_extract_attom_id_missing():
    assert attom_mapper.extract_attom_id({}) is None


def test_extract_lat_lon():
    lat, lon = attom_mapper.extract_lat_lon(ADDRESS_RESP)
    assert lat == pytest.approx(32.7767)
    assert lon == pytest.approx(-96.797)


def test_extract_zip():
    assert attom_mapper.extract_zip(ADDRESS_RESP) == "75201"


def test_map_property_partial():
    detail = {
        "property": [
            {
                "summary": {"yearBuilt": 2001, "propClass": "residential"},
                "building": {
                    "size": {"livingSize": 1800},
                    "rooms": {"beds": 3, "bathstotal": 2},
                    "stories": 1,
                    "construction": {"roofCover": "Shingle", "foundationType": "Slab"},
                },
            }
        ]
    }
    climate = {}
    result = attom_mapper.map_property(detail, climate)
    assert result["yearBuilt"] == 2001
    assert result["squareFootage"] == 1800.0
    assert result["numBedrooms"] == 3.0
    assert result["floodZone"] is None


def test_map_neighborhood_partial():
    nbhd = {
        "property": [
            {
                "community": {
                    "medianHouseholdIncome": 75000,
                    "unemploymentRate": 5.1,
                    "ownOccupied": 60.0,
                },
                "school": {"avgSchoolRating": 7.5},
                "crime": {"crimeIndex": 22.3},
            }
        ]
    }
    result = attom_mapper.map_neighborhood(nbhd)
    assert result["medianHouseholdIncome"] == 75000.0
    assert result["crimeStatistics"] == 22.3


def test_map_market_partial():
    market = {
        "saleSnapshot": [
            {
                "medianSaleAmt": 400000,
                "avgDomSale": 35,
                "pctChgMedianSaleAmt": 2.5,
            }
        ]
    }
    rental = {}
    result = attom_mapper.map_market(market, rental)
    assert result["medianHomeValue"] == 400000.0
    assert result["daysOnMarket"] == 35
    assert result["rentPrices"] is None
