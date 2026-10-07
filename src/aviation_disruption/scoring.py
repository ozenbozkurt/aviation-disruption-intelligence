"""Explainable baseline disruption-risk scoring.

This module intentionally uses a transparent heuristic rather than a trained
model. It is suitable for demos, tests, and portfolio development—not for
operational safety decisions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class RiskInput:
    wind_kts: float
    visibility_km: float
    precipitation_mm_h: float
    historical_delay_rate: float
    historical_cancel_rate: float


@dataclass(frozen=True)
class RiskAssessment:
    score: float
    band: str
    drivers: tuple[str, ...]
    components: dict[str, float]

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["drivers"] = list(self.drivers)
        return data


def _validate(features: RiskInput) -> None:
    for name in ("wind_kts", "visibility_km", "precipitation_mm_h"):
        value = getattr(features, name)
        if value < 0:
            raise ValueError(f"{name} must be non-negative")

    for name in ("historical_delay_rate", "historical_cancel_rate"):
        value = getattr(features, name)
        if not 0 <= value <= 1:
            raise ValueError(f"{name} must be between 0 and 1")


def _bounded(value: float, low: float, high: float) -> float:
    return max(low, min(value, high))


def assess_risk(features: RiskInput) -> RiskAssessment:
    """Return an explainable 0–100 disruption-risk assessment."""
    _validate(features)

    wind = _bounded(features.wind_kts - 15.0, 0.0, 30.0)

    if features.visibility_km >= 10:
        visibility = 0.0
    elif features.visibility_km <= 1:
        visibility = 25.0
    else:
        visibility = ((10.0 - features.visibility_km) / 9.0) * 25.0

    precipitation = _bounded(features.precipitation_mm_h / 10.0 * 20.0, 0.0, 20.0)
    delay_history = _bounded(features.historical_delay_rate / 0.5 * 20.0, 0.0, 20.0)
    cancel_history = _bounded(features.historical_cancel_rate / 0.1 * 5.0, 0.0, 5.0)

    components = {
        "wind": wind,
        "low_visibility": visibility,
        "precipitation": precipitation,
        "historical_delay_exposure": delay_history,
        "historical_cancellation_exposure": cancel_history,
    }

    score = round(sum(components.values()), 1)
    if score < 35:
        band = "LOW"
    elif score < 65:
        band = "MEDIUM"
    else:
        band = "HIGH"

    ranked = sorted(components.items(), key=lambda item: (-item[1], item[0]))
    drivers = tuple(name for name, value in ranked if value > 0)[:3]

    return RiskAssessment(
        score=score,
        band=band,
        drivers=drivers,
        components={name: round(value, 1) for name, value in components.items()},
    )
