"""Fetch a date range of real EUROCONTROL daily metrics into one CSV."""

from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path

from aviation_disruption.eurocontrol import EurocontrolDataClient
from aviation_disruption.exports import write_daily_network_csv_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a EUROCONTROL daily network date range to one CSV."
    )
    parser.add_argument("--country", required=True, help="Two-letter ISO code.")
    parser.add_argument("--start-date", required=True, type=date.fromisoformat)
    parser.add_argument("--end-date", required=True, type=date.fromisoformat)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def iter_days(start: date, end: date):
    if end < start:
        raise ValueError("end-date must be on or after start-date")

    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def main() -> None:
    args = parse_args()
    days = list(iter_days(args.start_date, args.end_date))

    metrics_rows = []
    with EurocontrolDataClient() as client:
        for index, day in enumerate(days, start=1):
            print(f"[{index}/{len(days)}] Fetching {args.country.upper()} {day}...")
            metrics_rows.append(
                client.get_daily_network_metrics(args.country, day)
            )

    output = write_daily_network_csv_rows(metrics_rows, args.output)
    print(f"Wrote {len(metrics_rows)} rows to {output}")


if __name__ == "__main__":
    main()
