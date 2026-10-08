import unittest

from aviation_disruption.live_api import app


class LiveDeploymentAppTests(unittest.TestCase):
    def test_expected_routes_are_registered_without_network_access(self):
        paths = {route.path for route in app.routes}
        self.assertIn("/health", paths)
        self.assertIn("/docs", paths)
        self.assertIn("/risk", paths)
        self.assertIn("/route-risk/{origin}/{dest}", paths)


if __name__ == "__main__":
    unittest.main()
