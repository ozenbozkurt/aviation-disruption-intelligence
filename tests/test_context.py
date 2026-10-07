from datetime import datetime, timezone
import unittest

from aviation_disruption.context import assess_context
from aviation_disruption.history import HistoricalRates
from aviation_disruption.weather import WeatherObservation


class ContextTests(unittest.TestCase):
    def test_weather_and_history_feed_same_explainable_engine(self):
        weather = WeatherObservation(
            "FRA",
            wind_kts=30,
            visibility_km=4,
            precipitation_mm_h=3,
            observed_at=datetime(2026, 10, 8, tzinfo=timezone.utc),
        )
        history = HistoricalRates(
            origin="FRA",
            dest="AMS",
            total_rows=100,
            operated_rows=98,
            delayed_rows=25,
            cancelled_rows=2,
            historical_delay_rate=0.25,
            historical_cancel_rate=0.02,
        )
        result = assess_context(weather, history)
        self.assertEqual(result.band, "MEDIUM")
        self.assertAlmostEqual(result.score, 48.7)


if __name__ == "__main__":
    unittest.main()
