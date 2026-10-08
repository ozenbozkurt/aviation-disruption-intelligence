"""Build a real EUROCONTROL CSV + Markdown case-study bundle."""

from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path

from aviation_disruption.case_study import (
    render_ai_explanation_prompt,
    render_case_study_markdown,
    summarize_network_period,
)
from aviation_disruption.eurocontrol import EurocontrolDataClient, EurocontrolDataError
from aviation_disruption.exports import write_daily_network_csv_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a recruiter-facing EUROCONTROL network case study."
    )
    parser.add_argument("--country", required=True, help="Two-letter ISO code.")
    parser.add_argument("--start-date", required=True, type=date.fromisoformat)
    parser.add_argument("--end-date", required=True, type=date.fromisoformat)
    parser.add_argument("--output-dir", required=True, type=Path)
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
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    missing_dates: list[str] = []
    days = list(iter_days(args.start_date, args.end_date))

    with EurocontrolDataClient() as client:
        for index, day in enumerate(days, start=1):
            print(f"[{index}/{len(days)}] Fetching {args.country.upper()} {day}...")
            try:
                rows.append(client.get_daily_network_metrics(args.country, day))
            except EurocontrolDataError as exc:
                missing_dates.append(day.isoformat())
                print(f"  skipped: {exc}")

    if not rows:
        raise SystemExit("No EUROCONTROL observations were retrieved")

    stem = (
        f"eurocontrol_{args.country.lower()}_"
        f"{args.start_date.isoformat()}_to_{args.end_date.isoformat()}"
    )
    csv_path = args.output_dir / f"{stem}.csv"
    report_path = args.output_dir / f"{stem}.md"
    prompt_path = args.output_dir / f"{stem}_ai_prompt.txt"

    write_daily_network_csv_rows(rows, csv_path)
    summary = summarize_network_period(rows)
    report_path.write_text(
        render_case_study_markdown(summary, missing_dates=missing_dates),
        encoding="utf-8",
    )
    prompt_path.write_text(
        render_ai_explanation_prompt(summary),
        encoding="utf-8",
    )

    print(f"Wrote {len(rows)} observations to {csv_path}")
    print(f"Wrote analyst brief to {report_path}")
    print(f"Wrote AI explanation prompt to {prompt_path}")


if __name__ == "__main__":
    main()
