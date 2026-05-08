from typing import Dict, Optional
from pydantic import BaseModel

from app.schemas.property_schema import PropertyEnrichResponse


class ScoreRequest(BaseModel):
    enrichedData: PropertyEnrichResponse
    userRanks: Dict[str, int]


class ScoreResponse(BaseModel):
    investmentScore: float
    scoreLabel: str
    variableScores: Dict[str, float]
    weights: Dict[str, float]
    weightedScores: Dict[str, float]
