from datetime import date
import unittest

from aviation_disruption.case_study import (
    render_ai_explanation_prompt,
    render_case_study_markdown,
    summarize_network_period,
)
from aviation_disruption.eurocontrol import DailyNetworkMetrics, EurocontrolCountry


class NetworkCaseStudyTests(unittest.TestCase):
    def _row(
        self,
        day: int,
        *,
        flights: float,
        delay: float,
        delay_per_flight: float,
        arrival: float,
        departure: float,
    ):
        return DailyNetworkMetrics(
            country=EurocontrolCountry(21, "Italy", "IT", "LI"),
            sync_id=500000 + day,
            sync_date=f"2026-03-{day:02d}T00:00:00+00:00",
            total_flights=flights,
            atfm_delay_minutes=delay,
            atfm_delay_per_flight_minutes=delay_per_flight,
            arrival_punctuality_percent=arrival,
            departure_punctuality_percent=departure,
        )

    def test_summary_identifies_highest_delay_per_flight_day(self):
        rows = [
            self._row(21, flights=5000, delay=200, delay_per_flight=0.04, arrival=82, departure=75),
            self._row(22, flights=5200, delay=600, delay_per_flight=0.12, arrival=70, departure=65),
            self._row(23, flights=5100, delay=300, delay_per_flight=0.06, arrival=79, departure=72),
        ]

        summary = summarize_network_period(rows)

        self.assertEqual(summary.observation_count, 3)
        self.assertEqual(summary.worst_day.sync_date[:10], "2026-03-22")
        self.assertEqual(summary.best_day.sync_date[:10], "2026-03-21")
        self.assertAlmostEqual(summary.average_daily_flights, 5100)
        self.assertAlmostEqual(summary.total_atfm_delay_minutes, 1100)

    def test_markdown_separates_observation_from_causes(self):
        rows = [
            self._row(21, flights=5000, delay=200, delay_per_flight=0.04, arrival=82, departure=75),
            self._row(22, flights=5200, delay=600, delay_per_flight=0.12, arrival=70, departure=65),
        ]
        summary = summarize_network_period(rows)
        report = render_case_study_markdown(summary, missing_dates=["2026-03-20"])

        self.assertIn("Highest-stress day", report)
        self.assertIn("2026-03-22", report)
        self.assertIn("Missing dates skipped: 2026-03-20", report)
        self.assertIn("not a flight-safety", report)

    def test_ai_prompt_forbids_invented_causes(self):
        rows = [
            self._row(21, flights=5000, delay=200, delay_per_flight=0.04, arrival=82, departure=75)
        ]
        prompt = render_ai_explanation_prompt(summarize_network_period(rows))

        self.assertIn("Do not invent causal explanations", prompt)
        self.assertIn("recruiter-facing takeaway", prompt)


if __name__ == "__main__":
    unittest.main()
