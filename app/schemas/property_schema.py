from typing import Optional
from pydantic import BaseModel


class PropertySchema(BaseModel):
    yearBuilt: Optional[int] = None
    constructionType: Optional[str] = None
    squareFootage: Optional[float] = None
    numBedrooms: Optional[float] = None
    numBathrooms: Optional[float] = None
    numFloors: Optional[int] = None
    roofType: Optional[str] = None
    foundationType: Optional[str] = None
    floodZone: Optional[str] = None
    hazardRiskZone: Optional[str] = None


class NeighborhoodSchema(BaseModel):
    medianHouseholdIncome: Optional[float] = None
    unemploymentRate: Optional[float] = None
    schoolRatings: Optional[float] = None
    crimeStatistics: Optional[float] = None
    homeownershipRate: Optional[float] = None


class MarketSchema(BaseModel):
    populationGrowth: Optional[float] = None
    medianHomeValue: Optional[float] = None
    homePriceAppreciationRate: Optional[float] = None
    daysOnMarket: Optional[int] = None
    rentPrices: Optional[float] = None
    zoningInformation: Optional[str] = None


class PropertyEnrichResponse(BaseModel):
    property: PropertySchema
    neighborhood: NeighborhoodSchema
    market: MarketSchema


class ErrorResponse(BaseModel):
    error: str
    provider: Optional[str] = None
