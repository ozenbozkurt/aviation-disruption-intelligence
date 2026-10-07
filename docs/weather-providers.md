# Weather provider design

The scoring core consumes normalized weather fields and must not know which
external service produced them.

## Normalized contract

Every provider returns a `WeatherObservation` with:

- airport identifier
- wind speed in knots
- visibility in kilometres
- precipitation intensity in millimetres per hour
- timezone-aware observation timestamp

This keeps provider-specific field names and units outside the scoring engine.

## Offline testing

`StaticWeatherProvider` is used for tests and local examples. CI never needs
network access or production credentials.

## Caching

`CachedWeatherProvider` adds a small in-memory TTL cache around any provider.
A live provider can therefore avoid repeated requests without changing the
consumer interface. This cache is deliberately process-local; persistent cache
storage can be added only if a real deployment requires it.

## Credentials

Provider credentials must be supplied at runtime through environment variables
or a deployment secret store. API keys must never be committed to this
repository, examples, fixtures, logs, or screenshots.

A future live-provider adapter should:

1. read credentials from the environment only when the selected provider needs them;
2. set explicit network timeouts;
3. convert provider units into the normalized contract;
4. map provider/network failures into clear application errors;
5. remain replaceable without changes to the scoring engine.


## Open-Meteo adapter

The optional `OpenMeteoWeatherProvider` uses the public forecast endpoint for
current gridded conditions at configured latitude/longitude coordinates.

The adapter explicitly requests wind speed in knots and precipitation in
millimetres, validates returned units, converts visibility from metres to
kilometres, uses a finite request timeout, and wraps transport/provider failures
in `WeatherProviderError`.

This integration is intended for software and analytics demonstrations. It is
not a replacement for aviation weather products such as METAR or TAF.
