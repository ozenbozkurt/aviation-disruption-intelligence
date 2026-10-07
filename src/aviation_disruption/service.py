"""End-to-end route-risk orchestration."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Protocol

from .context import assess_context
from .history import HistoricalRates
from .weather import WeatherProvider


class HistoricalFeatureProvider(Protocol):
    def route_rates(
        self,
        origin: str,
        dest: str,
        *,
        late_threshold: float = 15.0,
    ) -> HistoricalRates:
        """Return normalized historical rates for one route."""


@dataclass(frozen=True)
class RouteRiskResult:
    origin: str
    dest: str
    weather_observed_at: str
    wind_kts: float
    visibility_km: float
    precipitation_mm_h: float
    historical_delay_rate: float
    historical_cancel_rate: float
    historical_total_rows: int
    score: float
    band: str
    drivers: tuple[str, ...]
    components: dict[str, float]

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["drivers"] = list(self.drivers)
        return data


class RouteRiskService:
    """Compose weather, route history, and the explainable risk engine."""

    def __init__(
        self,
        weather_provider: WeatherProvider,
        history_provider: HistoricalFeatureProvider,
    ):
        self._weather = weather_provider
        self._history = history_provider

    def assess_route(self, origin: str, dest: str) -> RouteRiskResult:
        history = self._history.route_rates(origin, dest)
        weather = self._weather.get_observation(history.origin)
        assessment = assess_context(weather, history)

        return RouteRiskResult(
            origin=history.origin,
            dest=history.dest,
            weather_observed_at=weather.observed_at.isoformat(),
            wind_kts=weather.wind_kts,
            visibility_km=weather.visibility_km,
            precipitation_mm_h=weather.precipitation_mm_h,
            historical_delay_rate=history.historical_delay_rate,
            historical_cancel_rate=history.historical_cancel_rate,
            historical_total_rows=history.total_rows,
            score=assessment.score,
            band=assessment.band,
            drivers=assessment.drivers,
            components=assessment.components,
        )
