# Aviation Disruption Intelligence

[![Tests](https://github.com/ozenbozkurt/aviation-disruption-intelligence/actions/workflows/tests.yml/badge.svg)](https://github.com/ozenbozkurt/aviation-disruption-intelligence/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)

Explainable operational disruption-risk intelligence for aviation.

This project is being built as a portfolio-quality aviation data product: a transparent baseline risk engine first, followed by an API, a queryable data layer, weather integration, and evidence-based calibration.

## Why this project exists

Operational disruption is rarely driven by one factor. Weather, visibility, wind, and historical operating performance can all contribute to elevated risk. The goal is to combine those signals into a compact, explainable assessment that can support analysis and prioritization.

The current version is deliberately a **heuristic baseline**, not a trained predictive model and not a safety-critical decision system.

## Current MVP

Input signals:

- wind speed in knots
- visibility in kilometres
- precipitation intensity
- historical delay rate
- historical cancellation rate

Output:

- a 0–100 disruption-risk score
- `LOW`, `MEDIUM`, or `HIGH` risk band
- the top contributing risk drivers
- component-level scores for transparency

## Quickstart

Requires Python 3.10+.

```sh
python -m venv .venv
python -m pip install -e ".[api,data,weather]"
```

Run the synthetic example:

```sh
aviation-risk \
  --wind-kts 30 \
  --visibility-km 4 \
  --precip-mm-h 3 \
  --delay-rate 0.25 \
  --cancel-rate 0.02
```

Example output shape:

```json
{
  "score": 48.7,
  "band": "MEDIUM",
  "drivers": [
    "low_visibility",
    "wind",
    "historical_delay_exposure"
  ],
  "components": {
    "wind": 15.0,
    "low_visibility": 16.7,
    "precipitation": 6.0,
    "historical_delay_exposure": 10.0,
    "historical_cancellation_exposure": 1.0
  }
}
```

## End-to-end route risk

The route service composes all current layers:

```text
route request
    |
    +--> historical route features (DuckDB)
    |
    +--> departure-airport weather (WeatherProvider)
    |
    +--> explainable scoring engine
    |
    +--> one route-risk response
```

An offline example can be served with synthetic data:

```sh
uvicorn examples.route_api:app --reload
```

Then request:

```sh
curl "http://127.0.0.1:8000/route-risk/FRA/AMS"
```

The response includes the risk score, band and drivers together with the weather timestamp and historical rates used to calculate it. This provenance is intentional: consumers should be able to see the main inputs behind the result.

The default application still exposes `/risk` for callers that supply their own features. `/route-risk/{origin}/{dest}` requires a configured `RouteRiskService`.

## Live weather provider

An optional Open-Meteo adapter can fetch current gridded weather for configured airport coordinates:

```python
from aviation_disruption.open_meteo import AirportCoordinates, OpenMeteoWeatherProvider

airports = {
    "FRA": AirportCoordinates(50.0379, 8.5622),
}

with OpenMeteoWeatherProvider(airports) as provider:
    observation = provider.get_observation("FRA")
    print(observation)
```

Install the weather extra with `python -m pip install -e ".[weather]"`.

The adapter requests wind in knots, visibility in metres (converted internally to kilometres), and precipitation in millimetres. Tests use mocked HTTP responses and do not call the public service.

**Important:** Open-Meteo returns gridded model weather. It is not an aerodrome METAR/TAF source and this project must not be used for dispatch, flight-safety, or go/no-go decisions.

## Weather adapter

Weather data enters the project through a provider-independent interface. Providers normalize observations to wind in knots, visibility in kilometres, precipitation in mm/h, and a timezone-aware timestamp.

Tests use an offline `StaticWeatherProvider`, while `CachedWeatherProvider` can wrap any future live provider with a small TTL cache. The scoring engine therefore stays independent of vendor APIs and credentials.

See [docs/weather-providers.md](docs/weather-providers.md) for the provider, caching, and secret-management strategy.

## EUROCONTROL Data app

The next data milestone integrates real European network-performance data from
the public EUROCONTROL Data app beta API. The first client increment resolves a
country and its date-specific Sync ID, which is the identifier used by later
traffic, delay and punctuality requests.

See [docs/eurocontrol-data.md](docs/eurocontrol-data.md) for the step-by-step
identifier flow and testing strategy.

## Power BI-ready export

A small example script can turn one real EUROCONTROL daily observation into a
flat CSV for Excel or Power BI:

```sh
python examples/export_eurocontrol_daily.py --country IT --date 2026-03-27 --output data/eurocontrol_it_2026-03-27.csv
```

See [docs/power-bi-handoff.md](docs/power-bi-handoff.md) for the beginner-friendly
API -> typed Python object -> CSV -> dashboard mental model.

## Historical data layer

The v0.3 data layer uses **DuckDB** to derive route-level historical features from a local CSV.

The included example is synthetic:

```python
from aviation_disruption.history import DuckDBHistoricalFeatureStore

with DuckDBHistoricalFeatureStore("examples/synthetic_history.csv") as store:
    rates = store.route_rates("FRA", "AMS")
    print(rates.historical_delay_rate)
    print(rates.historical_cancel_rate)
```

The SQL aggregation keeps operational definitions explicit:

- cancellation rate = cancelled rows / all route rows
- historical delay rate = operated flights delayed strictly more than the threshold / operated flights with a delay observation
- the default late threshold is 15 minutes

The feature store is local and deterministic. It does not download data or require credentials.

## HTTP API

Run the local API:

```sh
uvicorn aviation_disruption.api:app --reload
```

Then open `http://127.0.0.1:8000/docs` for the automatically generated OpenAPI interface.

Example request:

```sh
curl -X POST "http://127.0.0.1:8000/risk" \
  -H "Content-Type: application/json" \
  -d '{
    "wind_kts": 30,
    "visibility_km": 4,
    "precipitation_mm_h": 3,
    "historical_delay_rate": 0.25,
    "historical_cancel_rate": 0.02
  }'
```

The API and CLI call the same scoring engine, so the scoring semantics remain in one place.

## Scoring philosophy

The baseline is intentionally simple and inspectable:

- wind contributes up to 30 points
- low visibility up to 25
- precipitation up to 20
- historical delay exposure up to 20
- historical cancellation exposure up to 5

This makes every score explainable. Future ML work must beat this baseline on clearly defined evaluation data before replacing it.

## Tests

```sh
python -m unittest discover -s tests -v
```

GitHub Actions runs the suite on Windows and Linux using Python 3.10 and 3.12.

## Architecture direction

```text
Operational inputs
      |
      v
Feature validation
      |
      v
Explainable risk engine
      |
      +----> CLI (current)
      |
      +----> FastAPI (current)
      |
      +----> DuckDB feature store (current)
      |
      +----> Weather adapter (current)
```

See [ROADMAP.md](ROADMAP.md) for the staged build plan, [CHANGELOG.md](CHANGELOG.md) for maintained release changes, and [CONTRIBUTING.md](CONTRIBUTING.md) before proposing changes.

## Safety and limitations

This repository is an analytics and software-engineering project. The current score is **not validated for operational control, dispatch, flight safety, or go/no-go decisions**. Real-world use would require appropriate data quality controls, domain validation, calibration, governance, and human oversight.


## Hosted demo deployment

**Live API:** https://aviation-disruption-intelligence.onrender.com

**Interactive API docs:** https://aviation-disruption-intelligence.onrender.com/docs

The repository includes a Render Blueprint for a public portfolio demo. The
deployment entry point combines live Open-Meteo weather with the repository's
**synthetic** historical route fixture and exposes the existing FastAPI routes.

See [docs/deployment.md](docs/deployment.md) for the deployment configuration,
supported demo routes, and limitations.

## Release status

The first maintained public milestone is **v0.4.1**. See [RELEASE.md](RELEASE.md) for the release process. The project is not currently published to PyPI.
