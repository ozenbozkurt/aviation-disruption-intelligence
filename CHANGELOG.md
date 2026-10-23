# Changelog

All notable maintained changes to this project are documented here.

## v0.5.0 — 2026-10-23

Portfolio milestone focused on real European aviation operations data and recruiter-facing analysis.

### Added

- Official EUROCONTROL Data app beta API integration for country, daily traffic, ATFM delay and punctuality metrics.
- Multi-day real-data export workflow with explicit source/provenance fields.
- DuckDB persistence for normalized EUROCONTROL daily network observations.
- Power BI-ready CSV and Parquet outputs generated from the same normalized data.
- Automated GitHub Actions case-study workflow with downloadable artifacts.
- Transparent period-relative disruption index combining ATFM delay per flight and punctuality deterioration.
- Germany September 2026 network-performance case study using 30 real daily observations.
- Recruiter-facing live dashboard served from the hosted FastAPI application.

### Analytical discipline

- Traffic volume is contextual rather than treated as disruption by itself.
- Observations are separated from causal hypotheses; weather, ATC capacity, airport constraints and delay-cause data are identified as follow-up evidence rather than invented explanations.
- Real network data remains distinct from the synthetic route-history fixture used by the hosted route-risk demo.

### Safety and scope

The project remains an analytics and portfolio system. It is not validated for dispatch, operational control, flight safety or go/no-go decisions.


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
