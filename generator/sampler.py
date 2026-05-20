"""Explicit parameter sampler for preview generation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

DEFAULTS: dict[str, Any] = {
    "preview_count": 3,
    "seed": 20260520,
    "grid": False,
    "x_label": "Creep time",
    "x_unit": "h",
    "y_label": "Creep strain",
    "y_unit": "%",
    "x_range": [0, 1000],
    "num_curves": 3,
    "curve_shape": "near_linear",
    "points_per_curve": 160,
    "noise_level": 0.02,
    "line_style": "solid",
    "line_width": 1.5,
    "marker": "none",
    "legend_position": "inside_upper_right",
    "title": "Steel Creep Curves Preview",
}


def sample_parameters(mode: str, config: dict[str, Any] | None) -> dict[str, Any]:
    """Return explicit-mode parameters with defaults applied."""
    if mode != "explicit":
        raise ValueError("Only explicit mode is supported in V0 step 3")

    merged = deepcopy(DEFAULTS)
    if config:
        merged.update(config)

    merged["preview_count"] = max(3, min(int(merged["preview_count"]), 6))
    merged["num_curves"] = max(1, min(int(merged["num_curves"]), 4))
    merged["points_per_curve"] = max(50, min(int(merged["points_per_curve"]), 500))
    merged["noise_level"] = max(0.0, min(float(merged["noise_level"]), 0.1))
    merged["line_width"] = max(0.5, min(float(merged["line_width"]), 4.0))
    merged["seed"] = int(merged["seed"])
    return merged
