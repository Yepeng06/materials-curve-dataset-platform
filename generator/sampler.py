"""Explicit parameter sampler for preview generation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

DEFAULTS: dict[str, Any] = {
    "preview_count": 3,
    "num_curves": 3,
    "x_label": "Creep time",
    "x_unit": "h",
    "y_label": "Creep strain",
    "y_unit": "%",
    "x_range": [0, 1000],
    "curve_shape": "near_linear",
    "line_style": "solid",
    "marker": "none",
    "legend_position": "inside_upper_right",
    "grid": False,
    "seed": 20260520,
    "num_points": 140,
    "title": "Steel Creep Curves Preview",
}


def sample_parameters(mode: str, config: dict[str, Any] | None) -> dict[str, Any]:
    """Return explicit-mode parameters with defaults applied."""
    if mode != "explicit":
        raise ValueError("Only explicit mode is supported in V0 step 2")

    merged = deepcopy(DEFAULTS)
    if config:
        merged.update(config)

    merged["preview_count"] = int(merged["preview_count"])
    merged["preview_count"] = max(1, min(merged["preview_count"], 6))
    merged["num_curves"] = max(1, min(int(merged["num_curves"]), 4))
    merged["num_points"] = max(20, int(merged["num_points"]))
    return merged
