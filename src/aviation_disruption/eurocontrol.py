"""Small client for the public EUROCONTROL Data app beta API.

The client is intentionally narrow: first resolve a country, then resolve the
snapshot ("sync") for one date. Higher-level traffic and delay retrieval can be
built on top of those stable identifiers.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import httpx


class EurocontrolDataError(RuntimeError):
    """Raised when the EUROCONTROL Data app cannot return usable data."""


@dataclass(frozen=True)
class EurocontrolCountry:
    id: int
    name: str
    iso2: str
    icao: str | None = None


@dataclass(frozen=True)
class EurocontrolSync:
    id: int
    country: EurocontrolCountry
    sync_date: str
    app_updated: str | None
    data_type: str | None
    code: str | None


@dataclass(frozen=True)
class DailyNetworkMetrics:
    """Headline network-performance values for one country and one day."""

    country: EurocontrolCountry
    sync_id: int
    sync_date: str
    total_flights: float
    atfm_delay_minutes: float
    atfm_delay_per_flight_minutes: float
    arrival_punctuality_percent: float
    departure_punctuality_percent: float


class EurocontrolDataClient:
    """Read public network-performance data from the EUROCONTROL Data app."""

    BASE_URL = "https://api-data-app.eurocontrol.int/api"

    def __init__(
        self,
        *,
        timeout_seconds: float = 10.0,
        client: httpx.Client | None = None,
    ):
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=timeout_seconds)
        self._country_cache: dict[str, EurocontrolCountry] = {}

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "EurocontrolDataClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _get_collection(self, path: str, params: dict[str, object]) -> list[dict[str, Any]]:
        try:
            response = self._client.get(f"{self.BASE_URL}/{path}", params=params)
            response.raise_for_status()
            payload = response.json()
            data = payload["data"]
            if not isinstance(data, list):
                raise TypeError("data must be a list")
            return data
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            raise EurocontrolDataError(
                f"EUROCONTROL Data app request failed for {path}"
            ) from exc

    def get_country(self, iso2: str) -> EurocontrolCountry:
        code = iso2.strip().upper()
        if len(code) != 2 or not code.isalpha():
            raise ValueError("iso2 must be a two-letter country code")

        cached = self._country_cache.get(code)
        if cached is not None:
            return cached

        rows = self._get_collection("countries", {"iso2": code})
        if not rows:
            raise EurocontrolDataError(f"No country found for ISO2 code {code}")

        row = rows[0]
        try:
            country = EurocontrolCountry(
                id=int(row["id"]),
                name=str(row["name"]),
                iso2=str(row["iso2"]).upper(),
                icao=str(row["icao"]) if row.get("icao") is not None else None,
            )
            self._country_cache[code] = country
            return country
        except (KeyError, TypeError, ValueError) as exc:
            raise EurocontrolDataError(
                f"Malformed country response for ISO2 code {code}"
            ) from exc

    @staticmethod
    def _network_value(
        rows: list[dict[str, Any]],
        *,
        parent_key: str,
        network_type: str,
    ) -> float:
        for row in rows:
            parent = row.get(parent_key) or {}
            if (
                parent.get("rankingCategory") == "network"
                and row.get("networkType") == network_type
                and row.get("dateRange") == "DY"
                and row.get("value") is not None
            ):
                try:
                    return float(row["value"])
                except (TypeError, ValueError) as exc:
                    raise EurocontrolDataError(
                        f"Malformed {parent_key} network value"
                    ) from exc

        raise EurocontrolDataError(
            f"No daily network value found for {parent_key}/{network_type}"
        )

    def get_sync(self, iso2: str, day: date) -> EurocontrolSync:
        country = self.get_country(iso2)
        day_text = day.isoformat()
        rows = self._get_collection(
            "syncs",
            {
                "country.id": country.id,
                "syncDate[before]": day_text,
                "syncDate[after]": day_text,
            },
        )
        if not rows:
            raise EurocontrolDataError(
                f"No EUROCONTROL snapshot found for {country.iso2} on {day_text}"
            )

        row = rows[0]
        try:
            returned_country = row.get("country") or {}
            normalized_country = EurocontrolCountry(
                id=int(returned_country.get("id", country.id)),
                name=str(returned_country.get("name", country.name)),
                iso2=str(returned_country.get("iso2", country.iso2)).upper(),
                icao=(
                    str(returned_country["icao"])
                    if returned_country.get("icao") is not None
                    else country.icao
                ),
            )
            return EurocontrolSync(
                id=int(row["id"]),
                country=normalized_country,
                sync_date=str(row["syncDate"]),
                app_updated=(
                    str(row["appUpdated"])
                    if row.get("appUpdated") is not None
                    else None
                ),
                data_type=(
                    str(row["dataType"]) if row.get("dataType") is not None else None
                ),
                code=str(row["code"]) if row.get("code") is not None else None,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise EurocontrolDataError(
                f"Malformed sync response for {country.iso2} on {day_text}"
            ) from exc

    def get_daily_network_metrics(
        self,
        iso2: str,
        day: date,
    ) -> DailyNetworkMetrics:
        """Return headline traffic, ATFM-delay and punctuality metrics."""

        sync = self.get_sync(iso2, day)

        traffic_rows = self._get_collection(
            "traffic_networks",
            {"traffic.sync.id": sync.id},
        )
        delay_rows = self._get_collection(
            "delay_networks",
            {"delay.sync.id": sync.id},
        )
        punctuality_rows = self._get_collection(
            "punctualities_networks",
            {"punctuality.sync.id": sync.id},
        )

        return DailyNetworkMetrics(
            country=sync.country,
            sync_id=sync.id,
            sync_date=sync.sync_date,
            total_flights=self._network_value(
                traffic_rows,
                parent_key="traffic",
                network_type="total",
            ),
            atfm_delay_minutes=self._network_value(
                delay_rows,
                parent_key="delay",
                network_type="total",
            ),
            atfm_delay_per_flight_minutes=self._network_value(
                delay_rows,
                parent_key="delay",
                network_type="avg",
            ),
            arrival_punctuality_percent=self._network_value(
                punctuality_rows,
                parent_key="punctuality",
                network_type="total",
            ),
            departure_punctuality_percent=self._network_value(
                punctuality_rows,
                parent_key="punctuality",
                network_type="avg",
            ),
        )
