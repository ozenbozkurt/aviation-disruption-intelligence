"""Fetch one real EUROCONTROL daily observation and export it to CSV."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from aviation_disruption.eurocontrol import EurocontrolDataClient
from aviation_disruption.exports import write_daily_network_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export one EUROCONTROL daily network observation to CSV."
    )
    parser.add_argument(
        "--country",
        required=True,
        help="Two-letter ISO country code, for example IT or DE.",
    )
    parser.add_argument(
        "--date",
        required=True,
        type=date.fromisoformat,
        help="Observation date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="CSV file path to create.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    with EurocontrolDataClient() as client:
        metrics = client.get_daily_network_metrics(args.country, args.date)

    output = write_daily_network_csv(metrics, args.output)
    print(f"Wrote {output}")
    print(
        f"{metrics.country.iso2} {args.date}: "
        f"{metrics.total_flights:.0f} flights, "
        f"{metrics.atfm_delay_minutes:.0f} ATFM-delay minutes, "
        f"{metrics.arrival_punctuality_percent:.2f}% arrival punctuality"
    )


if __name__ == "__main__":
    main()
