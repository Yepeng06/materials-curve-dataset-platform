"""Parameter sampler for explicit and probabilistic preview generation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import numpy as np

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

SUPPORTED_PROB_FIELDS = [
    "num_curves",
    "curve_shape",
    "line_style",
    "marker",
    "legend_position",
    "grid",
]


def _validate_common(merged: dict[str, Any]) -> dict[str, Any]:
    merged["preview_count"] = max(3, min(int(merged["preview_count"]), 6))
    merged["num_curves"] = max(1, min(int(merged["num_curves"]), 4))
    merged["points_per_curve"] = max(50, min(int(merged["points_per_curve"]), 500))
    merged["noise_level"] = max(0.0, min(float(merged["noise_level"]), 0.1))
    merged["line_width"] = max(0.5, min(float(merged["line_width"]), 4.0))
    merged["seed"] = int(merged["seed"])
    return merged


def _choice_by_distribution(
    rng: np.random.Generator,
    distribution: dict[str, float] | None,
    fallback: Any,
) -> Any:
    if not distribution:
        return fallback
    keys = list(distribution.keys())
    probs = np.array([float(distribution[k]) for k in keys], dtype=float)
    total = probs.sum()
    if total <= 0:
        return fallback
    probs = probs / total
    return keys[int(rng.choice(len(keys), p=probs))]


def sample_parameters(
    mode: str,
    config: dict[str, Any] | None,
    template_data: dict[str, Any] | None = None,
    sample_index: int = 0,
) -> dict[str, Any]:
    """Sample preview parameters from explicit config or template distributions."""
    merged = deepcopy(DEFAULTS)

    template_defaults = (template_data or {}).get("default_parameters", {})
    if template_defaults:
        merged.update(template_defaults)

    incoming = deepcopy(config or {})
    incoming.pop("mode", None)
    incoming.pop("template_id", None)
    mode = mode or "explicit"
    if mode not in {"explicit", "probabilistic"}:
        raise ValueError(f"Unsupported mode: {mode}")

    if mode == "probabilistic":
        for field in SUPPORTED_PROB_FIELDS:
            incoming.pop(field, None)
    merged.update(incoming)

    sampled_parameters: dict[str, Any] = {}
    if mode == "probabilistic":
        distributions = (template_data or {}).get("probability_distributions", {})
        base_seed = int(merged.get("seed", DEFAULTS["seed"]))
        rng = np.random.default_rng(base_seed + sample_index)
        for field in SUPPORTED_PROB_FIELDS:
            sampled_value = _choice_by_distribution(
                rng,
                distributions.get(field),
                merged.get(field),
            )
            sampled_parameters[field] = sampled_value
            merged[field] = sampled_value

    merged = _validate_common(merged)
    merged["mode"] = mode
    merged["sampled_parameters"] = sampled_parameters
    merged["actual_parameters"] = {
        key: merged[key]
        for key in [
            "num_curves",
            "curve_shape",
            "line_style",
            "marker",
            "legend_position",
            "grid",
            "points_per_curve",
            "noise_level",
            "line_width",
            "seed",
        ]
        if key in merged
    }
    return merged
