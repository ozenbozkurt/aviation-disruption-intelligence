import unittest

from fastapi.testclient import TestClient

from aviation_disruption.api import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

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
