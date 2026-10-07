"""Open-Meteo implementation of the weather provider contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping

import httpx

from .weather import WeatherObservation


@dataclass(frozen=True)
class AirportCoordinates:
    latitude: float
    longitude: float


class WeatherProviderError(RuntimeError):
    """Raised when a live weather provider cannot return a valid observation."""


class OpenMeteoWeatherProvider:
    """Fetch normalized current weather from Open-Meteo by airport coordinates."""

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(
        self,
        airport_coordinates: Mapping[str, AirportCoordinates],
        *,
        timeout_seconds: float = 5.0,
        client: httpx.Client | None = None,
    ):
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

        self._airports = {
            code.strip().upper(): coords
            for code, coords in airport_coordinates.items()
        }
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=timeout_seconds)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "OpenMeteoWeatherProvider":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def get_observation(self, airport: str) -> WeatherObservation:
        code = airport.strip().upper()
        try:
            coords = self._airports[code]
        except KeyError as exc:
            raise ValueError(f"No coordinates configured for airport {code}") from exc

        params = {
            "latitude": coords.latitude,
            "longitude": coords.longitude,
            "current": "wind_speed_10m,visibility,precipitation",
            "wind_speed_unit": "kn",
            "precipitation_unit": "mm",
            "timezone": "GMT",
        }

        try:
            response = self._client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise WeatherProviderError(
                f"Open-Meteo request failed for airport {code}"
            ) from exc

        try:
            current = payload["current"]
            units = payload["current_units"]

            if units["wind_speed_10m"] != "kn":
                raise WeatherProviderError("Unexpected wind-speed unit")
            if units["visibility"] != "m":
                raise WeatherProviderError("Unexpected visibility unit")
            if units["precipitation"] != "mm":
                raise WeatherProviderError("Unexpected precipitation unit")

            observed_at = datetime.fromisoformat(current["time"])
            if observed_at.tzinfo is None:
                observed_at = observed_at.replace(tzinfo=timezone.utc)

            return WeatherObservation(
                airport=code,
                wind_kts=float(current["wind_speed_10m"]),
                visibility_km=float(current["visibility"]) / 1000.0,
                precipitation_mm_h=float(current["precipitation"]),
                observed_at=observed_at,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise WeatherProviderError(
                f"Malformed Open-Meteo response for airport {code}"
            ) from exc
