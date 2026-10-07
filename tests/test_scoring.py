import unittest

from aviation_disruption import RiskInput, assess_risk


class RiskScoringTests(unittest.TestCase):
    def test_low_risk_case(self):
        result = assess_risk(RiskInput(10, 10, 0, 0.05, 0.0))
        self.assertEqual(result.band, "LOW")
        self.assertLess(result.score, 35)

    def test_high_risk_case_is_explainable(self):
        result = assess_risk(RiskInput(45, 1, 10, 0.5, 0.1))
        self.assertEqual(result.band, "HIGH")
        self.assertEqual(result.score, 100.0)
        self.assertEqual(result.drivers[0], "wind")
        self.assertEqual(len(result.drivers), 3)

    def test_invalid_rate_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "historical_delay_rate"):
            assess_risk(RiskInput(10, 10, 0, 1.2, 0.0))

    def test_negative_weather_input_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "wind_kts"):
            assess_risk(RiskInput(-1, 10, 0, 0.1, 0.0))


if __name__ == "__main__":
    unittest.main()
