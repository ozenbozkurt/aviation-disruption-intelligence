"""Run an offline end-to-end route-risk API using synthetic data."""

from datetime import datetime, timezone
from pathlib import Path

from aviation_disruption.api import create_app
from aviation_disruption.history import DuckDBHistoricalFeatureStore
from aviation_disruption.service import RouteRiskService
from aviation_disruption.weather import StaticWeatherProvider, WeatherObservation


ROOT = Path(__file__).resolve().parents[1]
history = DuckDBHistoricalFeatureStore(ROOT / "examples" / "synthetic_history.csv")
weather = StaticWeatherProvider(
    {
        "FRA": WeatherObservation(
            "FRA",
            wind_kts=30,
            visibility_km=4,
            precipitation_mm_h=3,
            observed_at=datetime.now(timezone.utc),
        )
    }
)

app = create_app(RouteRiskService(weather, history))
