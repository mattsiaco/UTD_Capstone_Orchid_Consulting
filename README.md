# Property Enrichment API

A FastAPI backend that accepts a U.S. property address and returns enriched property, neighborhood, and market data by aggregating multiple external data sources.

---

## What It Does

Given a property address, the API returns a structured JSON response covering three categories:

**Property**
- Year built, construction type, square footage, bedrooms, bathrooms, floors
- Roof type, foundation type, flood zone, hazard risk zone

**Neighborhood**
- Median household income, unemployment rate, homeownership rate
- School ratings, crime statistics

**Market**
- Median home value, home price appreciation rate, days on market
- Rent prices, population growth, zoning information

---

## Data Sources

| Field(s) | Source |
|---|---|
| All property characteristics | ATTOM Data Solutions (`expandedprofile`) |
| School ratings | ATTOM (`detailwithschools`) |
| Days on market, market sales data | RentCast API + ATTOM (`sale/snapshot`) |
| Rent prices | ATTOM AVM |
| Flood zone | FEMA National Flood Hazard Layer (NFHL) |
| Hazard risk zone | FEMA National Risk Index (NRI) |
| Median household income, unemployment rate, homeownership rate, median home value, population growth | U.S. Census Bureau ACS 5-Year Estimates |
| Zoning information | City/County ArcGIS zoning layers → ATTOM fallback → "Unknown" |

---

## Project Structure

```
Capstone Final 2026/
├── app/
│   ├── main.py                      # FastAPI app entry point
│   ├── api/
│   │   └── routes.py                # POST /v1/property/enrich endpoint
│   ├── services/
│   │   ├── enrichment_service.py    # Orchestrates all API calls
│   │   ├── attom_service.py         # ATTOM Data Solutions client
│   │   ├── census_service.py        # U.S. Census Bureau ACS client
│   │   ├── fema_service.py          # FEMA NFHL + NRI client
│   │   ├── rentcast_service.py      # RentCast API client
│   │   ├── geocoding_service.py     # Google Maps Geocoding client
│   │   └── zoning_service.py        # ArcGIS zoning layer client
│   ├── mappers/
│   │   └── attom_mapper.py          # Parses raw ATTOM responses into schema dicts
│   ├── schemas/
│   │   ├── property_schema.py       # Pydantic response models
│   │   └── request.py               # Pydantic request model
│   ├── utils/
│   │   └── logging.py               # Structured JSON logging + latency tracker
│   └── tests/
│       ├── test_routes.py
│       ├── test_mappers.py
│       └── test_census_service.py
├── .env.example                     # Template for environment variables
├── requirements.txt                 # Production dependencies
├── requirements-dev.txt             # Dev/test dependencies
├── Dockerfile
└── pytest.ini
```

---

## Prerequisites

- Python 3.10+
- API keys for the following services:

| Variable | Service | Required |
|---|---|---|
| `ATTOM_API_KEY` | [ATTOM Data Solutions](https://api.attomdata.com) | Yes |
| `RENTCAST_API_KEY` | [RentCast](https://app.rentcast.io/app/api-keys) | Yes |
| `GEOCODING_API_KEY` | [Google Maps Geocoding API](https://developers.google.com/maps/documentation/geocoding) | Yes |
| `CENSUS_API_KEY` | [U.S. Census Bureau](https://api.census.gov/data/key_signup.html) | No (rate-limited without) |

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd "Capstone Final 2026"
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example env file and fill in your API keys:

```bash
copy .env.example .env
```

Edit `.env`:

```env
ATTOM_API_KEY=your_attom_api_key_here
RENTCAST_API_KEY=your_rentcast_api_key_here
GEOCODING_API_KEY=your_google_maps_api_key_here
CENSUS_API_KEY=your_census_api_key_here   # optional
```

---

## Running the API

### Development (with auto-reload)

```bash
uvicorn app.main:app --reload --port 8000
```

### Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker build -t property-enrichment-api .
docker run -p 8000:8000 --env-file .env property-enrichment-api
```

The API will be available at `http://localhost:8000`.

Interactive docs (Swagger UI): `http://localhost:8000/docs`

---

## API Usage

### Endpoint

```
POST /v1/property/enrich
```

### Request

```json
{
  "address": "1234 Elm St, Dallas, TX 75218"
}
```

### Response

```json
{
  "property": {
    "yearBuilt": 1959,
    "constructionType": "Single Family Residence / Townhouse",
    "squareFootage": 2211,
    "numBedrooms": 3,
    "numBathrooms": 3,
    "numFloors": 1,
    "roofType": "Composition Shingle",
    "foundationType": "Slab",
    "floodZone": "X",
    "hazardRiskZone": "Relatively Moderate"
  },
  "neighborhood": {
    "medianHouseholdIncome": 72400,
    "unemploymentRate": 4.2,
    "schoolRatings": 2.47,
    "crimeStatistics": null,
    "homeownershipRate": 61.3
  },
  "market": {
    "populationGrowth": 3.1,
    "medianHomeValue": 310000,
    "homePriceAppreciationRate": 103.33,
    "daysOnMarket": 48,
    "rentPrices": 758640,
    "zoningInformation": "Single-Family Residential (R-7.5(A))"
  }
}
```

### Error Responses

| Status | Meaning |
|---|---|
| `404` | Address not found or could not be resolved by ATTOM |
| `422` | Invalid request body |
| `502` | Upstream provider returned an error or empty response |

### Example with curl

```bash
curl -X POST http://localhost:8000/v1/property/enrich \
  -H "Content-Type: application/json" \
  -d '{"address": "1234 Elm St, Dallas, TX 75218"}'
```

---

## Running Tests

Install dev dependencies first:

```bash
pip install -r requirements-dev.txt
```

Run all tests:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

---

## Health Check

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```
