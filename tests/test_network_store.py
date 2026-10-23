from pathlib import Path
import tempfile
import unittest

import duckdb

from aviation_disruption.eurocontrol import DailyNetworkMetrics, EurocontrolCountry
from aviation_disruption.network_store import DuckDBNetworkMetricsStore


class DuckDBNetworkMetricsStoreTests(unittest.TestCase):
    def _metrics(self, day: int, *, delay: float = 397.0):
        return DailyNetworkMetrics(
            country=EurocontrolCountry(21, "Italy", "IT", "LI"),
            sync_id=500400 + day,
            sync_date=f"2026-03-{day:02d}T00:00:00+00:00",
            total_flights=5586 + day,
            atfm_delay_minutes=delay,
            atfm_delay_per_flight_minutes=delay / (5586 + day),
            arrival_punctuality_percent=77.0152,
            departure_punctuality_percent=68.9177,
        )

    def test_store_persists_normalized_rows_with_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            database = Path(tmp) / "network.duckdb"
            with DuckDBNetworkMetricsStore(database) as store:
                written = store.upsert_many([self._metrics(27), self._metrics(28)])
                rows = store.rows()

            self.assertEqual(written, 2)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["country_iso2"], "IT")
            self.assertEqual(rows[0]["source"], "EUROCONTROL Data app beta API")
            self.assertTrue(str(rows[0]["sync_date"]).startswith("2026-03-27"))

    def test_same_country_and_source_date_is_replaced_not_duplicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            database = Path(tmp) / "network.duckdb"
            with DuckDBNetworkMetricsStore(database) as store:
                store.upsert_many([self._metrics(27, delay=397)])
                store.upsert_many([self._metrics(27, delay=999)])
                rows = store.rows()

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["atfm_delay_minutes"], 999)

    def test_parquet_export_can_be_queried_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            database = Path(tmp) / "network.duckdb"
            parquet = Path(tmp) / "network.parquet"

            with DuckDBNetworkMetricsStore(database) as store:
                store.upsert_many([self._metrics(27), self._metrics(28)])
                returned = store.export_parquet(parquet)

            self.assertEqual(returned, parquet)
            self.assertTrue(parquet.exists())

            connection = duckdb.connect()
            try:
                count, source = connection.execute(
                    "SELECT COUNT(*), MIN(source) FROM read_parquet(?)",
                    [str(parquet)],
                ).fetchone()
            finally:
                connection.close()

            self.assertEqual(count, 2)
            self.assertEqual(source, "EUROCONTROL Data app beta API")


if __name__ == "__main__":
    unittest.main()
