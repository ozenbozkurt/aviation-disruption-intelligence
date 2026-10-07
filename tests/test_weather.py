from datetime import datetime, timedelta, timezone
import unittest

from aviation_disruption.weather import (
    CachedWeatherProvider,
    StaticWeatherProvider,
    WeatherObservation,
)


NOW = datetime(2026, 10, 8, 0, 0, tzinfo=timezone.utc)


class CountingProvider:
    def __init__(self, observation):
        self.observation = observation
        self.calls = 0

    def get_observation(self, airport):
        self.calls += 1
        return self.observation


class WeatherAdapterTests(unittest.TestCase):
    def test_observation_normalizes_airport(self):
        observation = WeatherObservation(" fra ", 12, 8, 0.5, NOW)
        self.assertEqual(observation.airport, "FRA")

    def test_negative_weather_value_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "visibility_km"):
            WeatherObservation("FRA", 12, -1, 0, NOW)

    def test_naive_timestamp_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            WeatherObservation("FRA", 12, 8, 0, datetime(2026, 10, 8))

    def test_static_provider_is_offline_and_deterministic(self):
        observation = WeatherObservation("FRA", 18, 6, 1, NOW)
        provider = StaticWeatherProvider({"FRA": observation})
        self.assertEqual(provider.get_observation("fra"), observation)

    def test_cache_reuses_observation_until_ttl_expires(self):
        observation = WeatherObservation("FRA", 18, 6, 1, NOW)
        upstream = CountingProvider(observation)
        times = iter([NOW, NOW + timedelta(seconds=30), NOW + timedelta(seconds=61)])
        cached = CachedWeatherProvider(
            upstream,
            ttl_seconds=60,
            clock=lambda: next(times),
        )

        self.assertEqual(cached.get_observation("FRA"), observation)
        self.assertEqual(cached.get_observation("fra"), observation)
        self.assertEqual(upstream.calls, 1)

        self.assertEqual(cached.get_observation("FRA"), observation)
        self.assertEqual(upstream.calls, 2)


if __name__ == "__main__":
    unittest.main()
