"""Curve generators for steel creep preview samples."""

from __future__ import annotations

from typing import List
import numpy as np


DataPoints = List[list[float]]


def _smooth_noise(noise: np.ndarray) -> np.ndarray:
    kernel = np.array([0.08, 0.18, 0.48, 0.18, 0.08], dtype=float)
    return np.convolve(noise, kernel, mode="same")


def _shape_base_slope(curve_shape: str, t: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Create base positive slope profile by curve shape."""
    if curve_shape == "primary_obvious":
        early_boost = rng.uniform(1.35, 1.95)
        decay = rng.uniform(2.2, 3.6)
        mild_floor = rng.uniform(0.35, 0.65)
        return mild_floor + early_boost * np.exp(-decay * t)

    if curve_shape == "accelerated_obvious":
        base = rng.uniform(0.25, 0.6)
        accel = rng.uniform(1.6, 2.8)
        power = rng.uniform(1.8, 3.0)
        late_push = rng.uniform(0.3, 0.8) * np.power(np.clip(t - 0.55, 0.0, 1.0), 1.4)
        return base + accel * np.power(t, power) + late_push

    if curve_shape == "three_stage":
        primary = 0.5 + 1.2 * np.exp(-3.2 * t)
        steady = 0.42 + 0.04 * np.sin(2.0 * np.pi * t)
        tertiary = 1.5 * np.power(np.clip(t - 0.62, 0.0, 1.0), 1.7)
        return primary + steady + tertiary

    if curve_shape == "irregular":
        trend = 0.72 + 0.26 * t
        wave = 0.08 * np.sin(8 * np.pi * t + rng.uniform(0.0, 2.0 * np.pi))
        return trend + wave

    # near_linear (default)
    slope = rng.uniform(0.75, 1.25)
    bend = rng.uniform(-0.22, 0.25)
    return slope + bend * (t - 0.5)


def _integrate_slope_to_curve(
    slope: np.ndarray,
    y_start: float,
    y_end: float,
) -> np.ndarray:
    slope = np.maximum(slope, 1e-4)
    y_raw = np.cumsum(slope)
    y_raw -= y_raw[0]
    denom = max(float(y_raw[-1]), 1e-9)
    y_norm = y_raw / denom
    return y_start + y_norm * max(y_end - y_start, 1e-6)


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

    y_start = float(rng.uniform(0.003, 0.08))
    y_end = float(rng.uniform(0.35, 1.08))
    if y_end <= y_start + 0.08:
        y_end = y_start + float(rng.uniform(0.18, 0.75))

    base_slope = _shape_base_slope(curve_shape, t, rng)
    jitter = rng.normal(0.0, max(noise_level, 0.0025) * 0.22, size=num_points)
    smooth_jitter = _smooth_noise(jitter)
    local_trend = rng.uniform(-0.08, 0.08) * (t - 0.5)
    slope = base_slope * (1.0 + smooth_jitter + local_trend)

    y = _integrate_slope_to_curve(slope=slope, y_start=y_start, y_end=y_end)
    return [[float(xv), float(yv)] for xv, yv in zip(x, y)]
