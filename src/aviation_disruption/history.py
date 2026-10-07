"""DuckDB-backed historical feature calculations."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import duckdb


@dataclass(frozen=True)
class HistoricalRates:
    origin: str
    dest: str
    total_rows: int
    operated_rows: int
    delayed_rows: int
    cancelled_rows: int
    historical_delay_rate: float
    historical_cancel_rate: float


class DuckDBHistoricalFeatureStore:
    """Query route-level historical rates from a local CSV using DuckDB."""

    REQUIRED_COLUMNS = {"origin", "dest", "dep_delay", "cancelled"}

    def __init__(self, csv_path: str | Path):
        self.csv_path = Path(csv_path)
        if not self.csv_path.is_file():
            raise ValueError(f"Historical CSV not found: {self.csv_path}")

        self._conn = duckdb.connect(":memory:")
        self._load_csv()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "DuckDBHistoricalFeatureStore":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _load_csv(self) -> None:
        with self.csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = set(reader.fieldnames or [])
            missing = sorted(self.REQUIRED_COLUMNS - columns)
            if missing:
                raise ValueError(
                    "Missing required historical columns: " + ", ".join(missing)
                )

            rows: list[tuple[str, str, float | None, int]] = []
            for line_number, row in enumerate(reader, start=2):
                origin = (row["origin"] or "").strip().upper()
                dest = (row["dest"] or "").strip().upper()
                if not origin or not dest:
                    raise ValueError(
                        f"origin and dest must be non-empty on line {line_number}"
                    )

                raw_cancelled = (row["cancelled"] or "").strip()
                try:
                    cancelled = int(raw_cancelled)
                except ValueError as exc:
                    raise ValueError(
                        f"cancelled must be 0 or 1 on line {line_number}"
                    ) from exc
                if cancelled not in (0, 1):
                    raise ValueError(
                        f"cancelled must be 0 or 1 on line {line_number}"
                    )

                raw_delay = (row["dep_delay"] or "").strip()
                if raw_delay == "":
                    dep_delay = None
                else:
                    try:
                        dep_delay = float(raw_delay)
                    except ValueError as exc:
                        raise ValueError(
                            f"dep_delay must be numeric or blank on line {line_number}"
                        ) from exc

                rows.append((origin, dest, dep_delay, cancelled))

        self._conn.execute(
            """
            CREATE TABLE flights (
                origin VARCHAR NOT NULL,
                dest VARCHAR NOT NULL,
                dep_delay DOUBLE,
                cancelled INTEGER NOT NULL
            )
            """
        )
        if rows:
            self._conn.executemany(
                "INSERT INTO flights VALUES (?, ?, ?, ?)",
                rows,
            )

    def route_rates(
        self,
        origin: str,
        dest: str,
        *,
        late_threshold: float = 15.0,
    ) -> HistoricalRates:
        if late_threshold < 0:
            raise ValueError("late_threshold must be non-negative")

        origin = origin.strip().upper()
        dest = dest.strip().upper()
        if not origin or not dest:
            raise ValueError("origin and dest must be non-empty")

        row = self._conn.execute(
            """
            SELECT
                COUNT(*) AS total_rows,
                COUNT(*) FILTER (WHERE cancelled = 0 AND dep_delay IS NOT NULL)
                    AS operated_rows,
                COUNT(*) FILTER (
                    WHERE cancelled = 0
                      AND dep_delay IS NOT NULL
                      AND dep_delay > ?
                ) AS delayed_rows,
                COUNT(*) FILTER (WHERE cancelled = 1) AS cancelled_rows
            FROM flights
            WHERE origin = ? AND dest = ?
            """,
            [late_threshold, origin, dest],
        ).fetchone()

        total_rows, operated_rows, delayed_rows, cancelled_rows = map(int, row)
        if total_rows == 0:
            raise ValueError(f"No historical rows found for route {origin}-{dest}")
        if operated_rows == 0:
            raise ValueError(
                f"No operated flights with delay observations for route {origin}-{dest}"
            )

        return HistoricalRates(
            origin=origin,
            dest=dest,
            total_rows=total_rows,
            operated_rows=operated_rows,
            delayed_rows=delayed_rows,
            cancelled_rows=cancelled_rows,
            historical_delay_rate=delayed_rows / operated_rows,
            historical_cancel_rate=cancelled_rows / total_rows,
        )
