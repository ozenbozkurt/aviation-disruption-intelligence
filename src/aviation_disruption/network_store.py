"""DuckDB persistence for normalized EUROCONTROL network observations."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import duckdb

from .eurocontrol import DailyNetworkMetrics
from .exports import CSV_COLUMNS, daily_network_row


TABLE_NAME = "eurocontrol_daily_network_metrics"


class DuckDBNetworkMetricsStore:
    """Persist daily EUROCONTROL network metrics with explicit provenance."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = duckdb.connect(str(self.database_path))
        self._connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                country_name VARCHAR NOT NULL,
                country_iso2 VARCHAR NOT NULL,
                country_icao VARCHAR NOT NULL,
                sync_id BIGINT NOT NULL,
                sync_date VARCHAR NOT NULL,
                total_flights DOUBLE NOT NULL,
                atfm_delay_minutes DOUBLE NOT NULL,
                atfm_delay_per_flight_minutes DOUBLE NOT NULL,
                arrival_punctuality_percent DOUBLE NOT NULL,
                departure_punctuality_percent DOUBLE NOT NULL,
                source VARCHAR NOT NULL,
                PRIMARY KEY (country_iso2, sync_date)
            )
            """
        )

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "DuckDBNetworkMetricsStore":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def upsert_many(self, metrics_rows: Iterable[DailyNetworkMetrics]) -> int:
        """Insert or replace normalized daily observations."""

        rows = [daily_network_row(metrics) for metrics in metrics_rows]
        if not rows:
            return 0

        placeholders = ", ".join("?" for _ in CSV_COLUMNS)
        columns = ", ".join(CSV_COLUMNS)

        for row in rows:
            self._connection.execute(
                f"""
                DELETE FROM {TABLE_NAME}
                WHERE country_iso2 = ? AND sync_date = ?
                """,
                [row["country_iso2"], row["sync_date"]],
            )
            self._connection.execute(
                f"INSERT INTO {TABLE_NAME} ({columns}) VALUES ({placeholders})",
                [row[column] for column in CSV_COLUMNS],
            )

        return len(rows)

    def count(self) -> int:
        """Return the number of persisted daily observations."""

        return int(
            self._connection.execute(
                f"SELECT COUNT(*) FROM {TABLE_NAME}"
            ).fetchone()[0]
        )

    def rows(self) -> list[dict[str, object]]:
        """Return stored rows ordered by source date."""

        cursor = self._connection.execute(
            f"""
            SELECT {", ".join(CSV_COLUMNS)}
            FROM {TABLE_NAME}
            ORDER BY sync_date
            """
        )
        names = [description[0] for description in cursor.description]
        return [dict(zip(names, row)) for row in cursor.fetchall()]

    def export_parquet(self, output_path: str | Path) -> Path:
        """Export the normalized table to a Power BI-friendly Parquet file."""

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        sql_path = path.resolve().as_posix().replace("'", "''")

        self._connection.execute(
            f"""
            COPY (
                SELECT {", ".join(CSV_COLUMNS)}
                FROM {TABLE_NAME}
                ORDER BY sync_date
            )
            TO '{sql_path}' (FORMAT PARQUET)
            """
        )
        return path
