"""CSV exports for recruiter-facing aviation analytics workflows."""

from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path

from .eurocontrol import DailyNetworkMetrics


CSV_COLUMNS = (
    "country_name",
    "country_iso2",
    "country_icao",
    "sync_id",
    "sync_date",
    "total_flights",
    "atfm_delay_minutes",
    "atfm_delay_per_flight_minutes",
    "arrival_punctuality_percent",
    "departure_punctuality_percent",
    "source",
)


def daily_network_row(metrics: DailyNetworkMetrics) -> dict[str, object]:
    """Flatten typed EUROCONTROL metrics into one Power BI-friendly row."""

    return {
        "country_name": metrics.country.name,
        "country_iso2": metrics.country.iso2,
        "country_icao": metrics.country.icao or "",
        "sync_id": metrics.sync_id,
        "sync_date": metrics.sync_date,
        "total_flights": metrics.total_flights,
        "atfm_delay_minutes": metrics.atfm_delay_minutes,
        "atfm_delay_per_flight_minutes": metrics.atfm_delay_per_flight_minutes,
        "arrival_punctuality_percent": metrics.arrival_punctuality_percent,
        "departure_punctuality_percent": metrics.departure_punctuality_percent,
        "source": "EUROCONTROL Data app beta API",
    }


def write_daily_network_csv(
    metrics: DailyNetworkMetrics,
    output_path: str | Path,
) -> Path:
    """Write one daily observation to a CSV that Excel/Power BI can import."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerow(daily_network_row(metrics))

    return path
