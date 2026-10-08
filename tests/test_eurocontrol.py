from datetime import date
import unittest

import httpx

from aviation_disruption.eurocontrol import (
    EurocontrolDataClient,
    EurocontrolDataError,
)


class EurocontrolDataClientTests(unittest.TestCase):
    def _client(self):
        def handler(request):
            if request.url.path.endswith("/countries"):
                self.assertEqual(request.url.params["iso2"], "IT")
                return httpx.Response(
                    200,
                    json={
                        "data": [
                            {
                                "id": 21,
                                "name": "Italy",
                                "iso2": "IT",
                                "icao": "LI",
                            }
                        ]
                    },
                    request=request,
                )

            if request.url.path.endswith("/syncs"):
                self.assertEqual(request.url.params["country.id"], "21")
                self.assertEqual(
                    request.url.params["syncDate[before]"], "2026-03-27"
                )
                self.assertEqual(
                    request.url.params["syncDate[after]"], "2026-03-27"
                )
                return httpx.Response(
                    200,
                    json={
                        "data": [
                            {
                                "id": 500450,
                                "country": {
                                    "id": 21,
                                    "name": "Italy",
                                    "iso2": "IT",
                                    "icao": "LI",
                                },
                                "syncDate": "2026-03-27T00:00:00+00:00",
                                "appUpdated": "2026-03-28T00:00:00+00:00",
                                "dataType": "state-specific",
                                "code": "IT",
                            }
                        ]
                    },
                    request=request,
                )

            return httpx.Response(404, request=request)

        return httpx.Client(transport=httpx.MockTransport(handler))

    def test_country_lookup_normalizes_iso2(self):
        client = self._client()
        provider = EurocontrolDataClient(client=client)
        country = provider.get_country("it")

        self.assertEqual(country.id, 21)
        self.assertEqual(country.name, "Italy")
        self.assertEqual(country.iso2, "IT")
        self.assertEqual(country.icao, "LI")
        client.close()

    def test_sync_lookup_uses_country_id_and_date(self):
        client = self._client()
        provider = EurocontrolDataClient(client=client)
        sync = provider.get_sync("IT", date(2026, 3, 27))

        self.assertEqual(sync.id, 500450)
        self.assertEqual(sync.country.iso2, "IT")
        self.assertEqual(sync.sync_date, "2026-03-27T00:00:00+00:00")
        self.assertEqual(sync.data_type, "state-specific")
        client.close()

    def test_bad_country_code_is_rejected_before_network(self):
        provider = EurocontrolDataClient(client=self._client())
        with self.assertRaisesRegex(ValueError, "two-letter"):
            provider.get_country("ITALY")
        provider._client.close()

    def test_missing_country_fails_clearly(self):
        def handler(request):
            return httpx.Response(200, json={"data": []}, request=request)

        client = httpx.Client(transport=httpx.MockTransport(handler))
        provider = EurocontrolDataClient(client=client)

        with self.assertRaisesRegex(EurocontrolDataError, "No country found"):
            provider.get_country("IT")
        client.close()


    def test_daily_network_metrics_combine_three_endpoints(self):
        def handler(request):
            path = request.url.path
            if path.endswith("/countries"):
                return httpx.Response(
                    200,
                    json={"data": [{"id": 21, "name": "Italy", "iso2": "IT", "icao": "LI"}]},
                    request=request,
                )
            if path.endswith("/syncs"):
                return httpx.Response(
                    200,
                    json={"data": [{
                        "id": 500450,
                        "country": {"id": 21, "name": "Italy", "iso2": "IT", "icao": "LI"},
                        "syncDate": "2026-03-27T00:00:00+00:00",
                        "appUpdated": "2026-03-28T00:00:00+00:00",
                        "dataType": "state-specific",
                        "code": "IT",
                    }]},
                    request=request,
                )
            if path.endswith("/traffic_networks"):
                self.assertEqual(request.url.params["traffic.sync.id"], "500450")
                return httpx.Response(
                    200,
                    json={"data": [
                        {
                            "traffic": {"rankingCategory": "network"},
                            "networkType": "total",
                            "dateRange": "DY",
                            "value": 5586,
                        }
                    ]},
                    request=request,
                )
            if path.endswith("/delay_networks"):
                self.assertEqual(request.url.params["delay.sync.id"], "500450")
                return httpx.Response(
                    200,
                    json={"data": [
                        {
                            "delay": {"rankingCategory": "network"},
                            "networkType": "total",
                            "dateRange": "DY",
                            "value": 397,
                        },
                        {
                            "delay": {"rankingCategory": "network"},
                            "networkType": "avg",
                            "dateRange": "DY",
                            "value": 0.0711,
                        },
                    ]},
                    request=request,
                )
            if path.endswith("/punctualities_networks"):
                self.assertEqual(request.url.params["punctuality.sync.id"], "500450")
                return httpx.Response(
                    200,
                    json={"data": [
                        {
                            "punctuality": {"rankingCategory": "network"},
                            "networkType": "total",
                            "dateRange": "DY",
                            "value": 77.0152,
                        },
                        {
                            "punctuality": {"rankingCategory": "network"},
                            "networkType": "avg",
                            "dateRange": "DY",
                            "value": 68.9177,
                        },
                    ]},
                    request=request,
                )
            return httpx.Response(404, request=request)

        client = httpx.Client(transport=httpx.MockTransport(handler))
        provider = EurocontrolDataClient(client=client)
        metrics = provider.get_daily_network_metrics("IT", date(2026, 3, 27))

        self.assertEqual(metrics.sync_id, 500450)
        self.assertEqual(metrics.total_flights, 5586)
        self.assertEqual(metrics.atfm_delay_minutes, 397)
        self.assertAlmostEqual(metrics.atfm_delay_per_flight_minutes, 0.0711)
        self.assertAlmostEqual(metrics.arrival_punctuality_percent, 77.0152)
        self.assertAlmostEqual(metrics.departure_punctuality_percent, 68.9177)
        client.close()

    def test_missing_daily_network_value_fails_clearly(self):
        rows = [
            {
                "delay": {"rankingCategory": "network"},
                "networkType": "total",
                "dateRange": "WK",
                "value": 397,
            }
        ]
        with self.assertRaisesRegex(EurocontrolDataError, "No daily network value"):
            EurocontrolDataClient._network_value(
                rows,
                parent_key="delay",
                network_type="total",
            )


    def test_country_lookup_is_cached_within_one_client(self):
        calls = {"countries": 0}

        def handler(request):
            if request.url.path.endswith("/countries"):
                calls["countries"] += 1
                return httpx.Response(
                    200,
                    json={"data": [{"id": 21, "name": "Italy", "iso2": "IT", "icao": "LI"}]},
                    request=request,
                )
            return httpx.Response(404, request=request)

        client = httpx.Client(transport=httpx.MockTransport(handler))
        provider = EurocontrolDataClient(client=client)

        first = provider.get_country("IT")
        second = provider.get_country("it")

        self.assertEqual(first, second)
        self.assertEqual(calls["countries"], 1)
        client.close()


if __name__ == "__main__":
    unittest.main()
