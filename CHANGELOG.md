# Changelog

All notable maintained changes to this project are documented here.

## v0.4.1 — 2026-10-08

First maintained public release of the end-to-end aviation disruption intelligence stack.

### Added

- Explainable 0–100 disruption-risk scoring with LOW / MEDIUM / HIGH bands.
- CLI JSON output and reusable Python scoring API.
- FastAPI service with typed validation and OpenAPI documentation.
- DuckDB-backed historical route feature calculations.
- Provider-independent weather observation contract and TTL cache wrapper.
- Optional Open-Meteo live weather provider with unit normalization and offline mocked tests.
- End-to-end route-risk orchestration combining weather, historical route features, and the scoring engine.
- Synthetic fixtures, regression tests, and GitHub Actions CI on Windows/Linux with Python 3.10/3.12.
- Roadmap, contribution guidance, issue/PR templates, and protected-main workflow.

### Safety and scope

The current risk score is a transparent heuristic baseline for analytics, software engineering, and portfolio demonstration. It is not validated for dispatch, operational control, flight-safety, or go/no-go decisions. Open-Meteo gridded weather is not a replacement for aviation METAR/TAF products.
