import unittest
from unittest.mock import Mock

from fastapi.testclient import TestClient

from aviation_disruption.api import app, create_app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root_is_portfolio_friendly(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["name"], "Aviation Disruption Intelligence")
        self.assertEqual(payload["docs"], "/docs")
        self.assertIn("not for flight-safety decisions", payload["scope"])

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_risk_endpoint_returns_explainable_score(self):
        response = self.client.post(
            "/risk",
            json={
                "wind_kts": 30,
                "visibility_km": 4,
                "precipitation_mm_h": 3,
                "historical_delay_rate": 0.25,
                "historical_cancel_rate": 0.02,
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["band"], "MEDIUM")
        self.assertAlmostEqual(payload["score"], 48.7)
        self.assertEqual(
            payload["drivers"],
            ["low_visibility", "wind", "historical_delay_exposure"],
        )
        self.assertIn("components", payload)

    def test_route_provider_failure_logs_safe_exception_types(self):
        try:
            raise TimeoutError("private upstream request data")
        except TimeoutError as underlying:
            failure = RuntimeError("private provider error message")
            failure.__cause__ = underlying

        service = Mock()
        service.assess_route.side_effect = failure
        with TestClient(create_app(service)) as client:
            with self.assertLogs("aviation_disruption.api", level="WARNING") as logs:
                response = client.get("/route-risk/FRA/AMS")

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), {"detail": "Weather provider is unavailable"})
        self.assertIn("error_type=RuntimeError cause_type=TimeoutError", logs.output[0])
        self.assertNotIn("private", logs.output[0])

    def test_invalid_rate_is_rejected_by_schema(self):
        response = self.client.post(
            "/risk",
            json={
                "wind_kts": 10,
                "visibility_km": 10,
                "precipitation_mm_h": 0,
                "historical_delay_rate": 1.1,
                "historical_cancel_rate": 0,
            },
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
