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


if __name__ == "__main__":
    unittest.main()
