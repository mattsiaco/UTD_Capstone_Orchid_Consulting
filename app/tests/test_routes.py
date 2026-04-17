"""
Integration-style tests using FastAPI's TestClient with mocked services.
Run with: pytest
"""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SAMPLE_ENRICHED = {
    "property": {
        "yearBuilt": 1998,
        "constructionType": "brick",
        "squareFootage": 2450.0,
        "numBedrooms": 4.0,
        "numBathrooms": 3.5,
        "numFloors": 2,
        "roofType": "Asphalt",
        "foundationType": "Slab",
        "floodZone": "X",
        "hazardRiskZone": None,
    },
    "neighborhood": {
        "medianHouseholdIncome": 92000.0,
        "unemploymentRate": 4.2,
        "schoolRatings": 8.1,
        "crimeStatistics": 14.2,
        "homeownershipRate": 62.5,
    },
    "market": {
        "populationGrowth": None,
        "medianHomeValue": 540000.0,
        "homePriceAppreciationRate": 3.1,
        "daysOnMarket": 28,
        "rentPrices": 2800.0,
        "zoningInformation": None,
    },
}


@patch(
    "app.services.enrichment_service.enrich",
    new_callable=AsyncMock,
    return_value=SAMPLE_ENRICHED,
)
def test_enrich_success(mock_enrich):
    resp = client.post("/v1/property/enrich", json={"address": "123 Main St, Dallas, TX 75201"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["property"]["yearBuilt"] == 1998
    assert body["neighborhood"]["medianHouseholdIncome"] == 92000.0
    assert body["market"]["medianHomeValue"] == 540000.0
    mock_enrich.assert_awaited_once_with("123 Main St, Dallas, TX 75201")


def test_enrich_missing_address():
    resp = client.post("/v1/property/enrich", json={"address": ""})
    assert resp.status_code == 422


def test_enrich_missing_body():
    resp = client.post("/v1/property/enrich", json={})
    assert resp.status_code == 422


@patch(
    "app.services.enrichment_service.enrich",
    new_callable=AsyncMock,
    side_effect=ValueError("Address not found via ATTOM"),
)
def test_enrich_address_not_found(mock_enrich):
    resp = client.post("/v1/property/enrich", json={"address": "999 Nowhere Blvd, Fake, TX"})
    assert resp.status_code == 404
    body = resp.json()
    assert "error" in body
    assert body["provider"] == "ATTOM"


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
