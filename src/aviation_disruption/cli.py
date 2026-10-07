"""Command-line interface for the baseline risk engine."""

from __future__ import annotations

import argparse
import json
import sys

from .scoring import RiskInput, assess_risk


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Score aviation disruption risk from operational inputs")
    p.add_argument("--wind-kts", type=float, required=True)
    p.add_argument("--visibility-km", type=float, required=True)
    p.add_argument("--precip-mm-h", type=float, required=True)
    p.add_argument("--delay-rate", type=float, required=True, help="Historical delay rate from 0 to 1")
    p.add_argument("--cancel-rate", type=float, required=True, help="Historical cancellation rate from 0 to 1")
    return p


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    try:
        assessment = assess_risk(
            RiskInput(
                wind_kts=args.wind_kts,
                visibility_km=args.visibility_km,
                precipitation_mm_h=args.precip_mm_h,
                historical_delay_rate=args.delay_rate,
                historical_cancel_rate=args.cancel_rate,
            )
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(assessment.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
