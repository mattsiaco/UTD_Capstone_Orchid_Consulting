import json
import traceback

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.property_schema import ErrorResponse, PropertyEnrichResponse
from app.schemas.request import EnrichRequest
from app.schemas.score_schema import ScoreRequest, ScoreResponse
from app.services import enrichment_service
from app.services.scoring_service import compute_investment_score
from app.config.scoring_config import DEFAULT_MIN_MAX_TABLE
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/v1/property", tags=["property"])


@router.post(
    "/enrich",
    response_model=PropertyEnrichResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        404: {"model": ErrorResponse, "description": "Address not found"},
        502: {"model": ErrorResponse, "description": "Upstream provider error"},
    },
    summary="Enrich a U.S. property address",
    description=(
        "Accepts a U.S. property address, fetches enrichment data from ATTOM "
        "(with FEMA and Census fallbacks), and returns a validated JSON schema "
        "containing property, neighborhood, and market data."
    ),
)
async def enrich_property(body: EnrichRequest) -> PropertyEnrichResponse:
    try:
        raw = await enrichment_service.enrich(body.address)
    except json.JSONDecodeError as exc:
        logger.error("empty/invalid response body from provider", extra={"extra": {"error": str(exc), "trace": traceback.format_exc()}})
        return JSONResponse(status_code=502, content={"error": "Provider returned an empty response", "detail": str(exc)})
    except ValueError as exc:
        return JSONResponse(status_code=404, content={"error": str(exc), "provider": "ATTOM"})
    except Exception as exc:
        logger.error("unhandled exception", extra={"extra": {"error": str(exc), "trace": traceback.format_exc()}})
        return JSONResponse(status_code=502, content={"error": "Upstream provider error", "detail": str(exc)})

    try:
        return PropertyEnrichResponse(**raw)
    except Exception as exc:
        logger.error("schema validation failed", extra={"extra": {"error": str(exc), "raw": str(raw)[:500]}})
        raise


@router.post(
    "/score",
    response_model=ScoreResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
    summary="Compute a weighted investment score",
    description=(
        "Accepts previously enriched property data and user importance rankings (1–5 per variable), "
        "applies the scoring algorithm, and returns a 0–100 investment score with per-variable breakdown."
    ),
)
async def score_property(body: ScoreRequest) -> ScoreResponse:
    enriched_data = {
        "property":     body.enrichedData.property.model_dump(),
        "neighborhood": body.enrichedData.neighborhood.model_dump(),
        "market":       body.enrichedData.market.model_dump(),
    }

    result = compute_investment_score(
        enriched_data=enriched_data,
        user_ranks=body.userRanks,
        min_max_table=DEFAULT_MIN_MAX_TABLE,
    )

    return ScoreResponse(**result)
