from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Property Enrichment API",
    description=(
        "MVP backend that accepts a U.S. property address, enriches it via "
        "ATTOM Data Solutions (with FEMA and Census fallbacks), and returns a "
        "validated JSON schema containing property, neighborhood, and market data."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(router)


@app.get("/health", tags=["ops"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
