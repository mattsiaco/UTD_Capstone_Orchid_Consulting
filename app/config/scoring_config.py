# Variable scoring rules and national reference ranges
#
# type "increase"    → higher value = better score (normalized 0-1)
# type "decrease"    → lower value  = better score (normalized 0-1)
# type "categorical" → value mapped to a fixed score via lookup table
# type "special"     → custom multi-bracket logic in scoring_service.py
#
# category must match the top-level key in the enriched data response:
#   "property" | "neighborhood" | "market"

VARIABLE_CONFIG: dict = {

    # ── Property ──────────────────────────────────────────────────────────────

    "yearBuilt": {
        "type": "increase",
        "category": "property",
    },
    "squareFootage": {
        "type": "increase",
        "category": "property",
    },
    "numBedrooms": {
        "type": "special",
        "category": "property",
    },
    "numBathrooms": {
        "type": "special",
        "category": "property",
    },
    "numFloors": {
        "type": "special",
        "category": "property",
    },
    "constructionType": {
        "type": "categorical",
        "category": "property",
        "scores": {
            "SINGLE FAMILY RESIDENCE / TOWNHOUSE": 0.90,
            "SINGLE FAMILY RESIDENCE":             0.90,
            "TOWNHOUSE":                           0.80,
            "CONDOMINIUM":                         0.70,
            "MULTI-FAMILY":                        0.75,
            "DUPLEX":                              0.70,
            "TRIPLEX":                             0.65,
            "QUADRUPLEX":                          0.65,
            "MOBILE HOME":                         0.40,
            "COMMERCIAL":                          0.30,
        },
        "default": 0.55,
    },
    "roofType": {
        "type": "categorical",
        "category": "property",
        "scores": {
            "METAL":                1.00,
            "TILE":                 0.90,
            "CONCRETE TILE":        0.90,
            "CLAY TILE":            0.85,
            "COMPOSITION SHINGLE":  0.80,
            "ASPHALT SHINGLE":      0.80,
            "SLATE":                0.95,
            "WOOD SHINGLE":         0.55,
            "WOOD SHAKE":           0.50,
            "BUILT-UP":             0.50,
            "FLAT":                 0.45,
            "ROLLED":               0.40,
            "OTHER":                0.50,
        },
        "default": 0.50,
    },
    "foundationType": {
        "type": "categorical",
        "category": "property",
        "scores": {
            "SLAB":           0.90,
            "BASEMENT":       0.85,
            "CRAWL SPACE":    0.70,
            "PIER AND BEAM":  0.60,
            "PIERS":          0.55,
            "OTHER":          0.50,
        },
        "default": 0.50,
    },
    "floodZone": {
        "type": "categorical",
        "category": "property",
        "scores": {
            "X":   1.00,   # minimal flood hazard
            "B":   0.80,   # moderate flood hazard (older designation)
            "C":   0.90,   # minimal (older designation)
            "D":   0.50,   # undetermined
            "A":   0.20,   # 100-yr flood zone
            "AE":  0.20,
            "AH":  0.25,
            "AO":  0.25,
            "AR":  0.30,
            "A99": 0.35,
            "V":   0.10,   # coastal high hazard
            "VE":  0.10,
        },
        "default": 0.50,
    },
    "hazardRiskZone": {
        "type": "categorical",
        "category": "property",
        "scores": {
            "VERY LOW":            1.00,
            "RELATIVELY LOW":      0.85,
            "RELATIVELY MODERATE": 0.55,
            "RELATIVELY HIGH":     0.30,
            "VERY HIGH":           0.10,
        },
        "default": 0.50,
    },

    # ── Neighborhood ──────────────────────────────────────────────────────────

    "medianHouseholdIncome": {
        "type": "increase",
        "category": "neighborhood",
    },
    "unemploymentRate": {
        "type": "decrease",
        "category": "neighborhood",
    },
    "schoolRatings": {
        "type": "increase",
        "category": "neighborhood",
    },
    "crimeStatistics": {
        "type": "decrease",
        "category": "neighborhood",
    },
    "homeownershipRate": {
        "type": "increase",
        "category": "neighborhood",
    },

    # ── Market ────────────────────────────────────────────────────────────────

    "populationGrowth": {
        "type": "increase",
        "category": "market",
    },
    "medianHomeValue": {
        "type": "special",
        "category": "market",
    },
    "homePriceAppreciationRate": {
        "type": "increase",
        "category": "market",
    },
    "daysOnMarket": {
        "type": "decrease",
        "category": "market",
    },
    "rentPrices": {
        "type": "increase",
        "category": "market",
    },
}


# National reference ranges used for min-max normalization.
# Based on approximate U.S. percentile distributions (5th–95th).
DEFAULT_MIN_MAX_TABLE: dict = {
    "yearBuilt":                {"min": 1940.0,  "max": 2023.0},
    "squareFootage":            {"min": 500.0,   "max": 5000.0},
    "medianHouseholdIncome":    {"min": 25000.0, "max": 120000.0},
    "unemploymentRate":         {"min": 2.0,     "max": 15.0},
    "schoolRatings":            {"min": 1.0,     "max": 4.3},
    "crimeStatistics":          {"min": 50.0,    "max": 800.0},
    "homeownershipRate":        {"min": 20.0,    "max": 85.0},
    "populationGrowth":         {"min": -5.0,    "max": 20.0},
    "homePriceAppreciationRate":{"min": 50.0,    "max": 500.0},
    "daysOnMarket":             {"min": 10.0,    "max": 120.0},
    "rentPrices":               {"min": 800.0,   "max": 5000.0},
}
