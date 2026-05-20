"""Curve generators for steel creep preview samples."""

from __future__ import annotations

from typing import List
import numpy as np


DataPoints = List[list[float]]


def _ensure_monotonic(y: np.ndarray) -> np.ndarray:
    """Force non-decreasing values to keep creep trend physically plausible."""
    return np.maximum.accumulate(y)


def generate_curve_data(
    curve_shape: str,
    x_min: float,
    x_max: float,
    num_points: int,
    noise_level: float,
    rng: np.random.Generator,
) -> DataPoints:
    """Generate monotonic creep-like curve points for a supported shape."""
    x = np.linspace(x_min, x_max, num_points)
    t = (x - x_min) / max(x_max - x_min, 1e-9)

    if curve_shape == "primary_obvious":
        y = 0.03 + 0.18 * np.sqrt(t + 1e-6) + 0.22 * t
    elif curve_shape == "accelerated_obvious":
        y = 0.02 + 0.08 * t + 0.60 * np.power(t, 2.6)
    else:  # near_linear default
        y = 0.03 + 0.35 * t + 0.03 * np.power(t, 1.8)

    noise = rng.normal(loc=0.0, scale=noise_level, size=num_points)
    y = _ensure_monotonic(y + noise)

    return [[float(xv), float(yv)] for xv, yv in zip(x, y)]
