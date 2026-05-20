"""Curve generation models for V0 preview."""

from __future__ import annotations

from typing import Literal

import numpy as np

CurveShape = Literal["near_linear", "primary_obvious", "accelerated_obvious"]


def _monotonicize(y: np.ndarray) -> np.ndarray:
    """Ensure mostly increasing creep trend with tiny minimum increments."""
    return np.maximum.accumulate(y)


def generate_curve_data(
    shape: CurveShape,
    point_count: int,
    x_range: tuple[float, float],
    y_base: float,
    y_span: float,
    rng: np.random.Generator,
) -> list[list[float]]:
    """Generate one creep-like curve with gentle noise and increasing trend."""
    point_count = max(16, int(point_count))
    x_min, x_max = x_range
    x = np.linspace(x_min, x_max, point_count)
    t = np.linspace(0.0, 1.0, point_count)

    if shape == "near_linear":
        core = y_base + y_span * (0.1 + 0.9 * t)
    elif shape == "primary_obvious":
        core = y_base + y_span * (0.15 + 0.85 * np.sqrt(t))
    elif shape == "accelerated_obvious":
        core = y_base + y_span * (0.05 + 0.95 * np.power(t, 2.2))
    else:
        raise ValueError(f"Unsupported curve shape: {shape}")

    noise = rng.normal(0.0, y_span * 0.01, size=point_count)
    y = _monotonicize(core + noise)
    y = np.clip(y, 0.0, None)

    return [[float(xv), float(yv)] for xv, yv in zip(x, y, strict=True)]


def generate_multi_curves(
    shape: CurveShape,
    num_curves: int,
    point_count: int,
    x_range: tuple[float, float],
    seed: int,
) -> list[list[list[float]]]:
    """Generate multiple creep curves for one chart."""
    rng = np.random.default_rng(seed)
    curves: list[list[list[float]]] = []
    n = max(1, min(4, int(num_curves)))
    for idx in range(n):
        base = 0.03 + idx * 0.06 + rng.uniform(0.0, 0.03)
        span = 0.6 + idx * 0.2 + rng.uniform(0.1, 0.3)
        curves.append(generate_curve_data(shape, point_count, x_range, base, span, rng))
    return curves
