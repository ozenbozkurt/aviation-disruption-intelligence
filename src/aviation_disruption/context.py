"""Compose historical and weather features for the risk engine."""

from __future__ import annotations

from .history import HistoricalRates
from .scoring import RiskAssessment, RiskInput, assess_risk
from .weather import WeatherObservation


def assess_context(
    weather: WeatherObservation,
    history: HistoricalRates,
) -> RiskAssessment:
    """Score one operational context without coupling providers to the model."""
    return assess_risk(
        RiskInput(
            wind_kts=weather.wind_kts,
            visibility_km=weather.visibility_km,
            precipitation_mm_h=weather.precipitation_mm_h,
            historical_delay_rate=history.historical_delay_rate,
            historical_cancel_rate=history.historical_cancel_rate,
        )
    )
