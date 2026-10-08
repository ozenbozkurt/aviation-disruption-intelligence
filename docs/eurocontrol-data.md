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
