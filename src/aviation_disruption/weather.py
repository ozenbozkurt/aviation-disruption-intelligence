"""Provider-independent weather observations for disruption analysis."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, Protocol


@dataclass(frozen=True)
class WeatherObservation:
    airport: str
    wind_kts: float
    visibility_km: float
    precipitation_mm_h: float
    observed_at: datetime

    def __post_init__(self) -> None:
        airport = self.airport.strip().upper()
        if not airport:
            raise ValueError("airport must be non-empty")
        object.__setattr__(self, "airport", airport)

        for name in ("wind_kts", "visibility_km", "precipitation_mm_h"):
            value = getattr(self, name)
            if value < 0:
                raise ValueError(f"{name} must be non-negative")

        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")


class WeatherProvider(Protocol):
    def get_observation(self, airport: str) -> WeatherObservation:
        """Return a normalized observation for one airport."""


class StaticWeatherProvider:
    """Offline provider backed by explicit observations."""

    def __init__(self, observations: dict[str, WeatherObservation]):
        self._observations = {
            airport.strip().upper(): observation
            for airport, observation in observations.items()
        }

    def get_observation(self, airport: str) -> WeatherObservation:
        key = airport.strip().upper()
        try:
            return self._observations[key]
        except KeyError as exc:
            raise ValueError(f"No weather observation configured for {key}") from exc


class CachedWeatherProvider:
    """Small in-memory TTL cache around any WeatherProvider."""

    def __init__(
        self,
        provider: WeatherProvider,
        *,
        ttl_seconds: int = 300,
        clock: Callable[[], datetime] | None = None,
    ):
        if ttl_seconds < 0:
            raise ValueError("ttl_seconds must be non-negative")
        self._provider = provider
        self._ttl = timedelta(seconds=ttl_seconds)
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._cache: dict[str, tuple[datetime, WeatherObservation]] = {}

    def get_observation(self, airport: str) -> WeatherObservation:
        key = airport.strip().upper()
        now = self._clock()
        if now.tzinfo is None:
            raise ValueError("cache clock must return a timezone-aware datetime")

        cached = self._cache.get(key)
        if cached is not None:
            stored_at, observation = cached
            if now - stored_at <= self._ttl:
                return observation

        observation = self._provider.get_observation(key)
        self._cache[key] = (now, observation)
        return observation
