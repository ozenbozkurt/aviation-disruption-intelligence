from datetime import datetime, timezone
from pathlib import Path
import unittest

from fastapi.testclient import TestClient

from aviation_disruption.api import create_app
from aviation_disruption.history import DuckDBHistoricalFeatureStore
from aviation_disruption.service import RouteRiskService
from aviation_disruption.weather import StaticWeatherProvider, WeatherObservation


FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "synthetic_history.csv"
NOW = datetime(2026, 10, 8, 0, 0, tzinfo=timezone.utc)


class RouteRiskApiTests(unittest.TestCase):
    def setUp(self):
        self.store = DuckDBHistoricalFeatureStore(FIXTURE)
        weather = StaticWeatherProvider(
            {
                "FRA": WeatherObservation(
                    "FRA",
                    wind_kts=30,
                    visibility_km=4,
                    precipitation_mm_h=3,
                    observed_at=NOW,
                )
            }
        )
        service = RouteRiskService(weather, self.store)
        self.client = TestClient(create_app(service))

    def tearDown(self):
        self.store.close()

    def test_route_risk_combines_weather_history_and_scoring(self):
        response = self.client.get("/route-risk/FRA/AMS")
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["origin"], "FRA")
        self.assertEqual(payload["dest"], "AMS")
        self.assertEqual(payload["weather_observed_at"], NOW.isoformat())
        self.assertAlmostEqual(payload["historical_delay_rate"], 0.5)
        self.assertAlmostEqual(payload["historical_cancel_rate"], 0.2)
        self.assertEqual(payload["historical_total_rows"], 5)
        self.assertEqual(payload["band"], "MEDIUM")
        self.assertAlmostEqual(payload["score"], 62.7)
        self.assertEqual(
            payload["drivers"],
            ["historical_delay_exposure", "low_visibility", "wind"],
        )

    def test_unknown_route_returns_404(self):
        response = self.client.get("/route-risk/JFK/LAX")
        self.assertEqual(response.status_code, 404)
        self.assertIn("No historical rows", response.json()["detail"])

    def test_unconfigured_route_service_returns_503(self):
        response = TestClient(create_app()).get("/route-risk/FRA/AMS")
        self.assertEqual(response.status_code, 503)


if __name__ == "__main__":
    unittest.main()
