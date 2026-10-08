from datetime import date
import unittest

from aviation_disruption.case_study import (
    build_period_relative_disruption_index,
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
        self.assertEqual(len(summary.daily_disruption_index), 3)
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
        self.assertIn("**Missing dates skipped:** 2026-03-20", report)
        self.assertIn("not a flight-safety", report)

    def test_ai_prompt_forbids_invented_causes(self):
        rows = [
            self._row(21, flights=5000, delay=200, delay_per_flight=0.04, arrival=82, departure=75)
        ]
        prompt = render_ai_explanation_prompt(summarize_network_period(rows))

        self.assertIn("Do not invent causal explanations", prompt)
        self.assertIn("recruiter-facing takeaway", prompt)


    def test_disruption_index_uses_delay_and_both_punctuality_metrics(self):
        rows = [
            self._row(21, flights=7000, delay=500, delay_per_flight=0.10, arrival=90, departure=90),
            self._row(22, flights=5000, delay=400, delay_per_flight=0.08, arrival=60, departure=55),
            self._row(23, flights=9000, delay=300, delay_per_flight=0.06, arrival=80, departure=78),
        ]

        index = build_period_relative_disruption_index(rows)
        score_by_date = {item.date: item.score for item in index}

        self.assertGreater(score_by_date["2026-03-22"], score_by_date["2026-03-21"])
        self.assertGreater(score_by_date["2026-03-22"], score_by_date["2026-03-23"])

    def test_traffic_volume_is_context_not_a_disruption_component(self):
        rows = [
            self._row(21, flights=4000, delay=200, delay_per_flight=0.05, arrival=80, departure=75),
            self._row(22, flights=9000, delay=200, delay_per_flight=0.05, arrival=80, departure=75),
        ]

        index = build_period_relative_disruption_index(rows)

        self.assertEqual(index[0].score, index[1].score)
        self.assertNotEqual(index[0].total_flights, index[1].total_flights)


if __name__ == "__main__":
    unittest.main()
