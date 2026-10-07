from datetime import timezone
import unittest

import httpx

from aviation_disruption.open_meteo import (
    AirportCoordinates,
    OpenMeteoWeatherProvider,
    WeatherProviderError,
)


class OpenMeteoProviderTests(unittest.TestCase):
    def _client(self, payload, status_code=200):
        def handler(request):
            self.assertIn("latitude", request.url.params)
            self.assertIn("longitude", request.url.params)
            self.assertEqual(request.url.params["wind_speed_unit"], "kn")
            return httpx.Response(status_code, json=payload, request=request)

        return httpx.Client(transport=httpx.MockTransport(handler))

    def test_current_weather_is_normalized(self):
        payload = {
            "current_units": {
                "time": "iso8601",
                "wind_speed_10m": "kn",
                "visibility": "m",
                "precipitation": "mm",
            },
            "current": {
                "time": "2026-10-08T00:00",
                "wind_speed_10m": 22.5,
                "visibility": 6500,
                "precipitation": 1.8,
            },
        }
        client = self._client(payload)
        provider = OpenMeteoWeatherProvider(
            {"FRA": AirportCoordinates(50.0379, 8.5622)},
            client=client,
        )
        observation = provider.get_observation("fra")

        self.assertEqual(observation.airport, "FRA")
        self.assertAlmostEqual(observation.wind_kts, 22.5)
        self.assertAlmostEqual(observation.visibility_km, 6.5)
        self.assertAlmostEqual(observation.precipitation_mm_h, 1.8)
        self.assertEqual(observation.observed_at.tzinfo, timezone.utc)
        client.close()

    def test_unknown_airport_is_rejected(self):
        provider = OpenMeteoWeatherProvider(
            {"FRA": AirportCoordinates(50.0379, 8.5622)},
            client=self._client({}),
        )
        with self.assertRaisesRegex(ValueError, "No coordinates configured"):
            provider.get_observation("AMS")
        provider._client.close()

    def test_http_failure_is_wrapped(self):
        provider = OpenMeteoWeatherProvider(
            {"FRA": AirportCoordinates(50.0379, 8.5622)},
            client=self._client({"error": True}, status_code=503),
        )
        with self.assertRaisesRegex(WeatherProviderError, "request failed"):
            provider.get_observation("FRA")
        provider._client.close()

    def test_unexpected_units_fail_clearly(self):
        payload = {
            "current_units": {
                "time": "iso8601",
                "wind_speed_10m": "km/h",
                "visibility": "m",
                "precipitation": "mm",
            },
            "current": {
                "time": "2026-10-08T00:00",
                "wind_speed_10m": 40,
                "visibility": 6500,
                "precipitation": 1.8,
            },
        }
        provider = OpenMeteoWeatherProvider(
            {"FRA": AirportCoordinates(50.0379, 8.5622)},
            client=self._client(payload),
        )
        with self.assertRaisesRegex(WeatherProviderError, "Unexpected wind-speed unit"):
            provider.get_observation("FRA")
        provider._client.close()


if __name__ == "__main__":
    unittest.main()
