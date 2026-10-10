import unittest

from fastapi.testclient import TestClient

from aviation_disruption.live_api import app


class LiveDeploymentAppTests(unittest.TestCase):
    def test_expected_routes_are_registered_without_network_access(self):
        paths = {route.path for route in app.routes}
        self.assertIn("/health", paths)
        self.assertIn("/docs", paths)
        self.assertIn("/risk", paths)
        self.assertIn("/route-risk/{origin}/{dest}", paths)
        self.assertIn("/dashboard/germany-september-2026", paths)


    def test_germany_dashboard_is_recruiter_facing(self):
        response = TestClient(app).get("/dashboard/germany-september-2026")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Germany Network Performance", response.text)
        self.assertIn("EUROCONTROL", response.text)
        self.assertIn("94.8/100", response.text)
        self.assertIn("Measurement first. Causal hypothesis second.", response.text)


if __name__ == "__main__":
    unittest.main()
