"""Curve generators for steel creep preview samples."""

from __future__ import annotations

from typing import List
import numpy as np

DataPoints = List[list[float]]


def _smooth_noise(noise: np.ndarray) -> np.ndarray:
    kernel = np.array([0.06, 0.18, 0.52, 0.18, 0.06], dtype=float)
    return np.convolve(noise, kernel, mode="same")


def _three_stage_profile(t: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    t1 = rng.uniform(0.2, 0.35)
    t2 = rng.uniform(0.62, 0.78)
    early_amp = rng.uniform(1.4, 2.1)
    early_decay = rng.uniform(3.0, 5.5)
    steady = rng.uniform(0.34, 0.58)
    tertiary_amp = rng.uniform(1.8, 3.2)
    tertiary_power = rng.uniform(1.3, 1.9)
    primary = early_amp * np.exp(-early_decay * np.clip(t / max(t1, 1e-6), 0.0, 1.0))
    tertiary = tertiary_amp * np.power(np.clip((t - t2) / max(1.0 - t2, 1e-6), 0.0, 1.0), tertiary_power)
    return 0.16 + primary + steady + tertiary


def _shape_base_slope(curve_shape: str, t: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    if curve_shape == "primary_obvious":
        return 0.22 + rng.uniform(1.2, 1.95) * np.exp(-rng.uniform(2.6, 4.2) * t)
    if curve_shape == "accelerated_obvious":
        base = rng.uniform(0.12, 0.34)
        gradual = rng.uniform(0.14, 0.36) * np.power(t, rng.uniform(1.2, 1.8))
        late = rng.uniform(1.3, 2.5) * np.power(np.clip(t - rng.uniform(0.58, 0.72), 0.0, 1.0), rng.uniform(1.4, 2.1))
        return base + gradual + late
    if curve_shape == "three_stage":
        return _three_stage_profile(t, rng)
    if curve_shape == "irregular":
        trend = 0.26 + 0.72 * t
        wave = 0.08 * np.sin(6.5 * np.pi * t + rng.uniform(0, 2 * np.pi)) + 0.05 * np.sin(13 * np.pi * t)
        return trend + wave
    slope = rng.uniform(0.7, 1.15)
    bend = rng.uniform(-0.16, 0.18)
    soft_curve = rng.uniform(-0.08, 0.14) * np.power(t - 0.5, 2)
    return slope + bend * (t - 0.5) + soft_curve


def _integrate_slope_to_curve(slope: np.ndarray, y_start: float, y_end: float) -> np.ndarray:
    slope = np.clip(slope, 1e-4, None)
    y_raw = np.cumsum(slope)
    y_raw -= y_raw[0]
    y_norm = y_raw / max(float(y_raw[-1]), 1e-9)
    return y_start + y_norm * max(y_end - y_start, 1e-6)


def generate_curve_data(curve_shape: str, x_min: float, x_max: float, num_points: int, noise_level: float, rng: np.random.Generator, curve_index: int = 0, total_curves: int = 1) -> DataPoints:
    x = np.linspace(x_min, x_max, num_points)
    t = (x - x_min) / max(x_max - x_min, 1e-9)

    curve_offset = (curve_index - max(total_curves - 1, 0) / 2.0) / max(total_curves, 1)
    y_start = float(rng.uniform(0.002, 0.05) + 0.015 * curve_offset)
    y_end = float(rng.uniform(0.42, 1.08) + 0.24 * curve_offset + 0.06 * curve_index)
    if y_end <= y_start + 0.12:
        y_end = y_start + float(rng.uniform(0.25, 0.92))

    base_slope = _shape_base_slope(curve_shape, t, rng)
    jitter = rng.normal(0.0, max(noise_level, 0.002) * 0.28, size=num_points)
    smooth_jitter = _smooth_noise(jitter)
    local_trend = (0.05 * curve_offset) * (t - 0.5)
    slope = base_slope * (1.0 + smooth_jitter + local_trend)
    y = _integrate_slope_to_curve(slope=slope, y_start=y_start, y_end=y_end)
    return [[float(xv), float(yv)] for xv, yv in zip(x, y)]
