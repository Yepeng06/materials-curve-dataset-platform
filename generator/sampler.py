"""Explicit-mode parameter sampler for V0 preview."""

from __future__ import annotations

from typing import Any

DEFAULTS: dict[str, Any] = {
    "preview_count": 3,
    "num_curves": 3,
    "x_label": "Creep time",
    "x_unit": "h",
    "y_label": "Creep strain",
    "y_unit": "%",
    "x_range": [0, 1000],
    "y_range": None,
    "curve_shape": "near_linear",
    "line_style": "solid",
    "marker": "none",
    "legend_position": "inside_upper_right",
    "grid": False,
    "seed": 20260520,
    "point_count": 120,
    "title": "Synthetic Steel Creep Curves",
}


def sample_parameters(mode: str, config: dict[str, Any] | None) -> dict[str, Any]:
    if mode != "explicit":
        raise ValueError("V0 currently supports explicit mode only")

    incoming = config or {}
    sampled = {**DEFAULTS, **incoming}
    sampled["preview_count"] = max(1, min(6, int(sampled["preview_count"])))
    sampled["num_curves"] = max(1, min(4, int(sampled["num_curves"])))
    sampled["seed"] = int(sampled["seed"])
    return sampled
