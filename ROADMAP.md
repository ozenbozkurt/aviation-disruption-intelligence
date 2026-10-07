# Roadmap

The project is intentionally developed as a sequence of small, testable vertical slices.

## v0.1 — Explainable baseline

- [x] Deterministic 0–100 disruption-risk score.
- [x] LOW / MEDIUM / HIGH risk band.
- [x] Explainable top risk drivers.
- [x] CLI output as JSON.
- [x] Unit tests and Windows/Linux CI.

## v0.2 — API

- [ ] Add a FastAPI service around the scoring engine.
- [ ] Add request/response validation and API tests.
- [ ] Publish a small OpenAPI usage example.

## v0.3 — Data layer

- [ ] Add DuckDB-backed historical flight features.
- [ ] Define a reproducible synthetic/local data pipeline.
- [ ] Separate raw inputs from derived operational features.

## v0.4 — Weather integration

- [ ] Add a weather-data adapter behind a stable interface.
- [ ] Cache and normalize weather observations.
- [ ] Keep external-provider credentials out of the repository.

## v0.5 — Calibration and evaluation

- [ ] Compare heuristic scores with observed disruption outcomes.
- [ ] Define train/validation time splits before introducing ML.
- [ ] Report calibration and error metrics instead of claiming predictive accuracy without evidence.

## Product direction

A compact aviation operations intelligence service that can answer:

> Given the current operational context for an airport or route, how elevated is disruption risk, and what are the main drivers?
