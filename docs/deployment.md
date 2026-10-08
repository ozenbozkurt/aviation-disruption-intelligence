# Render deployment

The repository includes a root-level `render.yaml` Blueprint for the hosted
portfolio demo.

## Service configuration

- Runtime: Python
- Python: 3.12
- Region: Frankfurt
- Plan: Free
- Health check: `/health`
- Auto-deploy: only after linked GitHub checks pass
- Start command:
  `uvicorn aviation_disruption.live_api:app --host 0.0.0.0 --port $PORT`

## Hosted demo data

The hosted route-risk endpoint intentionally combines:

- live gridded weather from Open-Meteo, and
- the repository's small synthetic historical route fixture.

The synthetic fixture currently demonstrates routes such as `FRA -> AMS`,
`FRA -> LHR`, and `AMS -> FRA`.

This design keeps the public demo reproducible and avoids publishing restricted
or unverified operational datasets.

## Limitations

Render Free web services can sleep when idle, so the first request after an
idle period can take longer. The hosted demo is a portfolio/analytics
demonstration and is not validated for dispatch, operational control, flight
safety, or go/no-go decisions.
