"""Small, deterministic summaries for EUROCONTROL portfolio case studies."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Sequence

from .eurocontrol import DailyNetworkMetrics


@dataclass(frozen=True)
class NetworkCaseStudySummary:
    country_name: str
    country_iso2: str
    start_date: str
    end_date: str
    observation_count: int
    average_daily_flights: float
    total_atfm_delay_minutes: float
    average_atfm_delay_per_flight_minutes: float
    average_arrival_punctuality_percent: float
    average_departure_punctuality_percent: float
    worst_day: DailyNetworkMetrics
    best_day: DailyNetworkMetrics


def summarize_network_period(
    rows: Sequence[DailyNetworkMetrics],
) -> NetworkCaseStudySummary:
    """Summarize one country's daily network metrics over a period."""

    if not rows:
        raise ValueError("At least one daily observation is required")

    country = rows[0].country
    if any(row.country.iso2 != country.iso2 for row in rows):
        raise ValueError("All observations must belong to the same country")

    ordered = sorted(rows, key=lambda row: row.sync_date)

    # Operational stress proxy for a simple recruiter-facing case study:
    # more ATFM delay per flight is worse; arrival punctuality breaks ties.
    worst = max(
        ordered,
        key=lambda row: (
            row.atfm_delay_per_flight_minutes,
            -row.arrival_punctuality_percent,
        ),
    )
    best = min(
        ordered,
        key=lambda row: (
            row.atfm_delay_per_flight_minutes,
            -row.arrival_punctuality_percent,
        ),
    )

    return NetworkCaseStudySummary(
        country_name=country.name,
        country_iso2=country.iso2,
        start_date=ordered[0].sync_date[:10],
        end_date=ordered[-1].sync_date[:10],
        observation_count=len(ordered),
        average_daily_flights=mean(row.total_flights for row in ordered),
        total_atfm_delay_minutes=sum(row.atfm_delay_minutes for row in ordered),
        average_atfm_delay_per_flight_minutes=mean(
            row.atfm_delay_per_flight_minutes for row in ordered
        ),
        average_arrival_punctuality_percent=mean(
            row.arrival_punctuality_percent for row in ordered
        ),
        average_departure_punctuality_percent=mean(
            row.departure_punctuality_percent for row in ordered
        ),
        worst_day=worst,
        best_day=best,
    )


def render_case_study_markdown(
    summary: NetworkCaseStudySummary,
    *,
    missing_dates: Sequence[str] = (),
) -> str:
    """Render an analyst-style Markdown brief from a period summary."""

    worst = summary.worst_day
    best = summary.best_day
    missing_text = (
        ", ".join(missing_dates)
        if missing_dates
        else "None"
    )

    return f"""# EUROCONTROL Network Performance Case Study — {summary.country_name}

## Executive snapshot

**Period:** {summary.start_date} to {summary.end_date}  
**Observed days:** {summary.observation_count}  
**Average daily flights:** {summary.average_daily_flights:,.0f}  
**Total ATFM delay:** {summary.total_atfm_delay_minutes:,.0f} minutes  
**Average ATFM delay per flight:** {summary.average_atfm_delay_per_flight_minutes:.3f} minutes  
**Average arrival punctuality:** {summary.average_arrival_punctuality_percent:.2f}%  
**Average departure punctuality:** {summary.average_departure_punctuality_percent:.2f}%

## Highest-stress day in the sample

**Date:** {worst.sync_date[:10]}  
**Flights:** {worst.total_flights:,.0f}  
**ATFM delay:** {worst.atfm_delay_minutes:,.0f} minutes  
**ATFM delay per flight:** {worst.atfm_delay_per_flight_minutes:.3f} minutes  
**Arrival punctuality:** {worst.arrival_punctuality_percent:.2f}%  
**Departure punctuality:** {worst.departure_punctuality_percent:.2f}%

For this baseline case study, the highest-stress day is defined by the largest
ATFM delay per flight, with lower arrival punctuality used only as a tie-breaker.
This is an analytical ranking rule, not a flight-safety or operational-control
decision rule.

## Lowest-stress day in the sample

**Date:** {best.sync_date[:10]}  
**ATFM delay per flight:** {best.atfm_delay_per_flight_minutes:.3f} minutes  
**Arrival punctuality:** {best.arrival_punctuality_percent:.2f}%

## Analyst interpretation prompts

1. Did the highest-stress day also have unusually high traffic volume?
2. Did arrival and departure punctuality deteriorate together?
3. Was the change mainly visible in ATFM delay per flight, or in total delay?
4. What external operational drivers should be checked next: weather, capacity,
   ATC restrictions, strikes, airport constraints, or demand peaks?
5. Would the signal have been visible early enough to support staffing,
   passenger-recovery, or disruption-management planning?

## Data quality and provenance

**Source:** EUROCONTROL Data app beta API  
**Missing dates skipped:** {missing_text}

This portfolio analysis is for learning and operational analytics only. It is
not validated for dispatch, flight-safety, or go/no-go decisions.
"""


def render_ai_explanation_prompt(summary: NetworkCaseStudySummary) -> str:
    """Create a compact prompt for an AI-assisted analyst explanation."""

    worst = summary.worst_day
    return f"""Act as a senior European aviation operations analyst.
Explain this EUROCONTROL network-performance period in clear professional English.

Country: {summary.country_name} ({summary.country_iso2})
Period: {summary.start_date} to {summary.end_date}
Observed days: {summary.observation_count}
Average daily flights: {summary.average_daily_flights:.0f}
Total ATFM delay minutes: {summary.total_atfm_delay_minutes:.0f}
Average ATFM delay per flight: {summary.average_atfm_delay_per_flight_minutes:.4f}
Average arrival punctuality: {summary.average_arrival_punctuality_percent:.2f}%
Average departure punctuality: {summary.average_departure_punctuality_percent:.2f}%
Highest-stress date by ATFM delay/flight: {worst.sync_date[:10]}
Highest-stress ATFM delay/flight: {worst.atfm_delay_per_flight_minutes:.4f}
Highest-stress arrival punctuality: {worst.arrival_punctuality_percent:.2f}%

Do not invent causal explanations. Separate observations from hypotheses.
Suggest the next operational data sources to investigate.
End with a 3-bullet recruiter-facing takeaway.
"""
