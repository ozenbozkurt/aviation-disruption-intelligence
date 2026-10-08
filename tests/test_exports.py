from pathlib import Path
import csv
import tempfile
import unittest

from aviation_disruption.eurocontrol import (
    DailyNetworkMetrics,
    EurocontrolCountry,
)
from aviation_disruption.exports import (
    CSV_COLUMNS,
    daily_network_row,
    write_daily_network_csv,
    write_daily_network_csv_rows,
)


class DailyNetworkExportTests(unittest.TestCase):
    def _metrics(self):
        return DailyNetworkMetrics(
            country=EurocontrolCountry(
                id=21,
                name="Italy",
                iso2="IT",
                icao="LI",
            ),
            sync_id=500450,
            sync_date="2026-03-27T00:00:00+00:00",
            total_flights=5586,
            atfm_delay_minutes=397,
            atfm_delay_per_flight_minutes=0.0711,
            arrival_punctuality_percent=77.0152,
            departure_punctuality_percent=68.9177,
        )

    def test_row_is_flat_and_has_provenance(self):
        row = daily_network_row(self._metrics())

        self.assertEqual(tuple(row), CSV_COLUMNS)
        self.assertEqual(row["country_iso2"], "IT")
        self.assertEqual(row["sync_id"], 500450)
        self.assertEqual(row["source"], "EUROCONTROL Data app beta API")

    def test_csv_can_be_read_back_as_one_flat_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "daily.csv"
            returned = write_daily_network_csv(self._metrics(), path)

            self.assertEqual(returned, path)
            with path.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["country_name"], "Italy")
        self.assertEqual(rows[0]["total_flights"], "5586")
        self.assertEqual(rows[0]["arrival_punctuality_percent"], "77.0152")


    def test_many_daily_rows_can_share_one_csv(self):
        first = self._metrics()
        second = DailyNetworkMetrics(
            country=first.country,
            sync_id=500451,
            sync_date="2026-03-28T00:00:00+00:00",
            total_flights=5600,
            atfm_delay_minutes=420,
            atfm_delay_per_flight_minutes=0.075,
            arrival_punctuality_percent=76.5,
            departure_punctuality_percent=68.2,
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "range.csv"
            write_daily_network_csv_rows([first, second], path)
            with path.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["sync_id"], "500450")
        self.assertEqual(rows[1]["sync_id"], "500451")


if __name__ == "__main__":
    unittest.main()
