"""Deployment entry point for the hosted portfolio demo.

The hosted demo intentionally combines live gridded weather with a small
synthetic historical route fixture. It is not an operational or safety system.
"""

from __future__ import annotations

from pathlib import Path

from .api import create_app
from .history import DuckDBHistoricalFeatureStore
from .open_meteo import AirportCoordinates, OpenMeteoWeatherProvider
from .service import RouteRiskService
from .weather import CachedWeatherProvider


ROOT = Path(__file__).resolve().parents[2]

AIRPORTS = {
    "FRA": AirportCoordinates(50.0379, 8.5622),
    "AMS": AirportCoordinates(52.3105, 4.7683),
    "LHR": AirportCoordinates(51.4700, -0.4543),
}

history = DuckDBHistoricalFeatureStore(ROOT / "examples" / "synthetic_history.csv")
weather = CachedWeatherProvider(
    OpenMeteoWeatherProvider(AIRPORTS, timeout_seconds=5.0),
    ttl_seconds=300,
)
app = create_app(RouteRiskService(weather, history))
