"""Example configuration for a live weather provider.

Coordinates are illustrative airport reference points for local experimentation.
Verify coordinates and source suitability before any real-world analysis.
"""

from aviation_disruption.open_meteo import AirportCoordinates, OpenMeteoWeatherProvider


AIRPORTS = {
    "FRA": AirportCoordinates(50.0379, 8.5622),
    "AMS": AirportCoordinates(52.3105, 4.7683),
    "LHR": AirportCoordinates(51.4700, -0.4543),
}


if __name__ == "__main__":
    with OpenMeteoWeatherProvider(AIRPORTS) as provider:
        print(provider.get_observation("FRA"))
