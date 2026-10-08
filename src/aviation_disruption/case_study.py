"""Small, deterministic summaries for EUROCONTROL portfolio case studies."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Sequence

from .eurocontrol import DailyNetworkMetrics


@dataclass(frozen=True)
class DailyDisruptionIndex:
    """Period-relative disruption score for one observed day."""

    date: str
    score: float
    atfm_delay_per_flight: float
    arrival_punctuality_percent: float
    departure_punctuality_percent: float
    total_flights: float


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
    daily_disruption_index: tuple[DailyDisruptionIndex, ...]



def _percentile_ranks(values: Sequence[float], *, reverse: bool = False) -> list[float]:
    """Return simple 0..1 average ranks within one observed period."""

    if not values:
        return []
    if len(values) == 1:
        return [0.0]

    ordered = sorted(values, reverse=reverse)
    positions: dict[float, list[int]] = {}
    for index, value in enumerate(ordered):
        positions.setdefault(value, []).append(index)

    average_position = {
        value: sum(indexes) / len(indexes)
        for value, indexes in positions.items()
    }
    denominator = len(values) - 1
    return [average_position[value] / denominator for value in values]


def build_period_relative_disruption_index(
    rows: Sequence[DailyNetworkMetrics],
) -> tuple[DailyDisruptionIndex, ...]:
    """Rank observed days using delay and punctuality, relative to the period.

    The index is intentionally period-relative rather than an absolute safety or
    operations threshold. Higher ATFM delay per flight is worse; lower arrival
    and departure punctuality are worse. Traffic volume is retained as context
    but not scored because high demand is not itself a disruption.
    """

    if not rows:
        return ()

    delay_rank = _percentile_ranks(
        [row.atfm_delay_per_flight_minutes for row in rows]
    )
    arrival_bad_rank = _percentile_ranks(
        [row.arrival_punctuality_percent for row in rows],
        reverse=True,
    )
    departure_bad_rank = _percentile_ranks(
        [row.departure_punctuality_percent for row in rows],
        reverse=True,
    )

    scored = []
    for row, delay, arrival, departure in zip(
        rows,
        delay_rank,
        arrival_bad_rank,
        departure_bad_rank,
    ):
        score = 100.0 * (
            0.50 * delay +
            0.25 * arrival +
            0.25 * departure
        )
        scored.append(
            DailyDisruptionIndex(
                date=row.sync_date[:10],
                score=round(score, 1),
                atfm_delay_per_flight=row.atfm_delay_per_flight_minutes,
                arrival_punctuality_percent=row.arrival_punctuality_percent,
                departure_punctuality_percent=row.departure_punctuality_percent,
                total_flights=row.total_flights,
            )
        )

    return tuple(sorted(scored, key=lambda item: item.date))


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
    index_rows = build_period_relative_disruption_index(ordered)
    score_by_date = {item.date: item.score for item in index_rows}

    worst = max(
        ordered,
        key=lambda row: score_by_date[row.sync_date[:10]],
    )
    best = min(
        ordered,
        key=lambda row: score_by_date[row.sync_date[:10]],
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
        daily_disruption_index=index_rows,
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

For this baseline case study, the highest-stress day is selected by a
**period-relative disruption index** combining ATFM delay per flight (50%),
arrival punctuality (25%) and departure punctuality (25%). Traffic volume is
shown as context but is not scored, because high traffic is not itself a
disruption. The index is relative to the selected period and is not a
flight-safety or operational-control decision rule.

## Lowest-stress day in the sample

**Date:** {best.sync_date[:10]}  
**ATFM delay per flight:** {best.atfm_delay_per_flight_minutes:.3f} minutes  
**Arrival punctuality:** {best.arrival_punctuality_percent:.2f}%

## Period-relative disruption index

| Date | Index | ATFM delay/flight | Arrival punctuality | Departure punctuality | Flights |
| --- | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(
    f"| {item.date} | {item.score:.1f} | {item.atfm_delay_per_flight:.3f} | "
    f"{item.arrival_punctuality_percent:.2f}% | "
    f"{item.departure_punctuality_percent:.2f}% | "
    f"{item.total_flights:,.0f} |"
    for item in summary.daily_disruption_index
)}

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
Highest-stress date by period-relative disruption index: {worst.sync_date[:10]}
Highest-stress ATFM delay/flight: {worst.atfm_delay_per_flight_minutes:.4f}
Highest-stress arrival punctuality: {worst.arrival_punctuality_percent:.2f}%
Highest-stress departure punctuality: {worst.departure_punctuality_percent:.2f}%

Do not invent causal explanations. Separate observations from hypotheses.
Suggest the next operational data sources to investigate.
End with a 3-bullet recruiter-facing takeaway.
"""
