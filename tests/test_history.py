from pathlib import Path
import tempfile
import unittest

from aviation_disruption.history import DuckDBHistoricalFeatureStore


FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "synthetic_history.csv"


class HistoricalFeatureStoreTests(unittest.TestCase):
    def test_route_rates_are_calculated_with_sql(self):
        with DuckDBHistoricalFeatureStore(FIXTURE) as store:
            rates = store.route_rates("fra", "ams")

        self.assertEqual(rates.total_rows, 5)
        self.assertEqual(rates.operated_rows, 4)
        self.assertEqual(rates.delayed_rows, 2)
        self.assertEqual(rates.cancelled_rows, 1)
        self.assertAlmostEqual(rates.historical_delay_rate, 0.5)
        self.assertAlmostEqual(rates.historical_cancel_rate, 0.2)

    def test_late_threshold_is_strictly_greater_than(self):
        with DuckDBHistoricalFeatureStore(FIXTURE) as store:
            rates = store.route_rates("FRA", "LHR", late_threshold=16)

        self.assertEqual(rates.delayed_rows, 0)

    def test_missing_route_fails_clearly(self):
        with DuckDBHistoricalFeatureStore(FIXTURE) as store:
            with self.assertRaisesRegex(ValueError, "No historical rows"):
                store.route_rates("JFK", "LAX")

    def test_missing_required_column_fails_clearly(self):
        content = "origin,dest,dep_delay\nFRA,AMS,12\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"
            path.write_text(content, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "cancelled"):
                DuckDBHistoricalFeatureStore(path)


if __name__ == "__main__":
    unittest.main()
