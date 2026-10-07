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
python -m pip install -e ".[api,data]"
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

## Weather adapter

Weather data enters the project through a provider-independent interface. Providers normalize observations to wind in knots, visibility in kilometres, precipitation in mm/h, and a timezone-aware timestamp.

Tests use an offline `StaticWeatherProvider`, while `CachedWeatherProvider` can wrap any future live provider with a small TTL cache. The scoring engine therefore stays independent of vendor APIs and credentials.

See [docs/weather-providers.md](docs/weather-providers.md) for the provider, caching, and secret-management strategy.

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

See [ROADMAP.md](ROADMAP.md) for the staged build plan and [CONTRIBUTING.md](CONTRIBUTING.md) before proposing changes.

## Safety and limitations

This repository is an analytics and software-engineering project. The current score is **not validated for operational control, dispatch, flight safety, or go/no-go decisions**. Real-world use would require appropriate data quality controls, domain validation, calibration, governance, and human oversight.
