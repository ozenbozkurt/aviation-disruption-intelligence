"""HTTP API for the disruption-risk engine."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .scoring import RiskInput, assess_risk

app = FastAPI(
    title="Aviation Disruption Intelligence",
    version="0.1.0",
    description=(
        "Explainable disruption-risk scoring for analytics and portfolio use. "
        "The current heuristic is not validated for safety-critical decisions."
    ),
)


class RiskRequest(BaseModel):
    wind_kts: float = Field(ge=0)
    visibility_km: float = Field(ge=0)
    precipitation_mm_h: float = Field(ge=0)
    historical_delay_rate: float = Field(ge=0, le=1)
    historical_cancel_rate: float = Field(ge=0, le=1)


class RiskResponse(BaseModel):
    score: float
    band: str
    drivers: list[str]
    components: dict[str, float]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/risk", response_model=RiskResponse)
def risk(payload: RiskRequest) -> RiskResponse:
    assessment = assess_risk(
        RiskInput(
            wind_kts=payload.wind_kts,
            visibility_km=payload.visibility_km,
            precipitation_mm_h=payload.precipitation_mm_h,
            historical_delay_rate=payload.historical_delay_rate,
            historical_cancel_rate=payload.historical_cancel_rate,
        )
    )
    return RiskResponse(**assessment.to_dict())
