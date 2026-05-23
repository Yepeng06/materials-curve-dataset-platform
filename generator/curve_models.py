"""Curve generators for steel creep preview samples."""

from __future__ import annotations

from typing import List
import numpy as np


DataPoints = List[list[float]]


def _smooth_noise(noise: np.ndarray) -> np.ndarray:
    kernel = np.array([0.2, 0.6, 0.2])
    return np.convolve(noise, kernel, mode="same")


def _light_monotonic_adjust(y: np.ndarray) -> np.ndarray:
    adjusted = y.copy()
    for i in range(1, len(adjusted)):
        if adjusted[i] < adjusted[i - 1]:
            adjusted[i] = adjusted[i - 1] + 1e-4
    return adjusted


def generate_curve_data(
    curve_shape: str,
    x_min: float,
    x_max: float,
    num_points: int,
    noise_level: float,
    rng: np.random.Generator,
) -> DataPoints:
    """Generate smooth creep-like curve points for a supported shape."""
    x = np.linspace(x_min, x_max, num_points)
    t = (x - x_min) / max(x_max - x_min, 1e-9)

    if curve_shape == "primary_obvious":
        y = 0.02 + 0.24 * np.sqrt(t + 1e-6) + 0.15 * t
    elif curve_shape == "accelerated_obvious":
        y = 0.02 + 0.08 * t + 0.55 * np.power(t, 2.4)
    else:  # near_linear
        y = 0.03 + 0.33 * t + 0.02 * np.power(t, 1.6)

    # Add per-curve amplitude shift so multi-curves do not fully overlap.
    scale = float(rng.uniform(0.92, 1.08))
    offset = float(rng.uniform(-0.008, 0.012))
    smooth_noise = _smooth_noise(rng.normal(0.0, noise_level * 0.45, size=num_points))
    y = _light_monotonic_adjust(y * scale + offset + smooth_noise)

    return [[float(xv), float(yv)] for xv, yv in zip(x, y)]
