# EUROCONTROL Data app integration

This integration starts deliberately small so each step is explainable and
testable.

## Mental model

Think of the API as a filing cabinet:

1. A **country code** such as `IT` finds the country record.
2. That country record has an internal **country ID** such as `21`.
3. For one date, the country ID finds a **Sync ID** (snapshot ID).
4. The Sync ID is then used to ask for traffic, ATFM delay and punctuality
   records belonging to that date.

The first implementation therefore adds only:

- `get_country("IT")`
- `get_sync("IT", date(...))`

Traffic and delay retrieval will be added in the next increment.

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
