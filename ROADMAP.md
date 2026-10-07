# Roadmap

The project is intentionally developed as a sequence of small, testable vertical slices.

## v0.1 — Explainable baseline

- [x] Deterministic 0–100 disruption-risk score.
- [x] LOW / MEDIUM / HIGH risk band.
- [x] Explainable top risk drivers.
- [x] CLI output as JSON.
- [x] Unit tests and Windows/Linux CI.

## v0.2 — API

- [x] Add a FastAPI service around the scoring engine.
- [x] Add request/response validation and API tests.
- [x] Publish a small OpenAPI usage example.

## v0.3 — Data layer

- [x] Add DuckDB-backed historical flight features.
- [x] Define a reproducible synthetic/local data pipeline.
- [x] Separate raw inputs from derived operational features.

## v0.4 — Weather integration

- [x] Add a weather-data adapter behind a stable interface.
- [x] Cache and normalize weather observations.
- [x] Keep external-provider credentials out of the repository.

## v0.4.1 — End-to-end route workflow

- [x] Compose weather and historical features behind one service.
- [x] Add a route-risk API endpoint with input provenance.
- [x] Keep end-to-end tests offline and deterministic.

## v0.5 — Calibration and evaluation

- [ ] Compare heuristic scores with observed disruption outcomes.
- [ ] Define train/validation time splits before introducing ML.
- [ ] Report calibration and error metrics instead of claiming predictive accuracy without evidence.

## Product direction

A compact aviation operations intelligence service that can answer:

> Given the current operational context for an airport or route, how elevated is disruption risk, and what are the main drivers?
