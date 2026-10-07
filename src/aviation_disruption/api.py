"""HTTP API for the disruption-risk engine."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .scoring import RiskInput, assess_risk
from .service import RouteRiskService


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


class RouteRiskResponse(RiskResponse):
    origin: str
    dest: str
    weather_observed_at: str
    wind_kts: float
    visibility_km: float
    precipitation_mm_h: float
    historical_delay_rate: float
    historical_cancel_rate: float
    historical_total_rows: int


def create_app(route_service: RouteRiskService | None = None) -> FastAPI:
    app = FastAPI(
        title="Aviation Disruption Intelligence",
        version="0.1.0",
        description=(
            "Explainable disruption-risk scoring for analytics and portfolio use. "
            "The current heuristic is not validated for safety-critical decisions."
        ),
    )

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

    @app.get("/route-risk/{origin}/{dest}", response_model=RouteRiskResponse)
    def route_risk(origin: str, dest: str) -> RouteRiskResponse:
        if route_service is None:
            raise HTTPException(
                status_code=503,
                detail="Route-risk service is not configured",
            )
        try:
            result = route_service.assess_route(origin, dest)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(
                status_code=502,
                detail="Weather provider is unavailable",
            ) from exc

        return RouteRiskResponse(**result.to_dict())

    return app


app = create_app()
