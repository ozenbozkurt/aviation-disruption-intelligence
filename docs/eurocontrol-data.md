# EUROCONTROL Data app integration

This integration is deliberately narrow and explainable: it focuses on
country-level daily network-performance metrics suitable for reproducible
portfolio analysis.

## Mental model

Think of the API as a filing cabinet:

1. A **country code** such as `IT` finds the country record.
2. That country record has an internal **country ID** such as `21`.
3. For one date, the country ID finds a **Sync ID** (snapshot ID).
4. The Sync ID is then used to ask for traffic, ATFM delay and punctuality
   records belonging to that date.

The implemented flow provides:

- `get_country("IT")`,
- `get_sync("IT", date(...))`,
- `get_daily_network_metrics("IT", date(...))`,
- normalized CSV export,
- DuckDB persistence,
- Parquet export for analytical handoff.

The daily metrics include total flights, total ATFM delay, ATFM delay per
flight, arrival punctuality and departure punctuality.

## Why tests do not call the internet

The tests use `httpx.MockTransport`. They imitate EUROCONTROL responses
locally, so CI stays deterministic and does not fail because an external API is
temporarily unavailable.

## Source

EUROCONTROL Data app beta API documentation:
https://data-app.eurocontrol.int/api

The public API is described as beta, so response validation and explicit error
messages are intentional.


## Step 2: headline daily network metrics

Once we have the Sync ID, the client can ask three endpoint families for one
day's headline values:

| Question | Endpoint | How the daily value is selected |
| --- | --- | --- |
| How many flights? | `traffic_networks` | network + total + DY |
| How much ATFM delay? | `delay_networks` | network + total + DY |
| ATFM delay per flight? | `delay_networks` | network + avg + DY |
| Arrival punctuality? | `punctualities_networks` | network + total + DY |
| Departure punctuality? | `punctualities_networks` | network + avg + DY |

For the EUROCONTROL documentation example (Italy, 2026-03-27), the published
example values include 5,586 flights, 397 ATFM-delay minutes, 0.0711 minutes of
ATFM delay per flight, 77.0152% arrival punctuality and 68.9177% departure
punctuality.

These semantics come from the EUROCONTROL Data app beta API documentation.


## Persistence and provenance

The case-study workflow stores normalized observations in the DuckDB table
`eurocontrol_daily_network_metrics`. The natural portfolio key is
`(country_iso2, sync_date)`, so rebuilding the same period replaces that
country/date observation rather than duplicating it.

Each row retains:

- country identifiers,
- EUROCONTROL `sync_id`,
- source timestamp `sync_date`,
- the five headline network metrics,
- explicit provenance: `EUROCONTROL Data app beta API`.

A Parquet export is generated from the persisted table for Power BI and other
analytical tools.

## Scope boundary

These are country-level network-performance observations. They should not be
presented as airline-specific, airport-specific or causal evidence. The project
uses them to identify patterns worth investigating; causal analysis requires
additional sources such as weather, ATC regulation/capacity, airport
constraints and delay-cause data.
