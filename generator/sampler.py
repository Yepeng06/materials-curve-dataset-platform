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
BOOL_FIELDS = {"grid"}
INT_FIELDS = {"num_curves", "points_per_curve", "preview_count", "seed"}
FLOAT_FIELDS = {"noise_level", "line_width"}
STRING_FIELDS = {"curve_shape", "line_style", "marker", "legend_position"}

TRACKED_ACTUAL_FIELDS = [
    "num_curves", "curve_shape", "line_style", "marker", "legend_position", "grid",
    "points_per_curve", "noise_level", "line_width", "x_label", "x_unit", "y_label", "y_unit", "seed",
]


def _validate_common(merged: dict[str, Any]) -> dict[str, Any]:
    merged["preview_count"] = max(3, min(int(merged["preview_count"]), 6))
    merged["num_curves"] = max(1, min(int(merged["num_curves"]), 5))
    merged["points_per_curve"] = max(50, min(int(merged["points_per_curve"]), 500))
    merged["noise_level"] = max(0.0, min(float(merged["noise_level"]), 0.1))
    merged["line_width"] = max(0.5, min(float(merged["line_width"]), 4.0))
    merged["seed"] = int(merged["seed"])
    return merged


def _choice_by_distribution(rng: np.random.Generator, distribution: dict[str, float] | None, fallback: Any) -> Any:
    if not distribution:
        return fallback
    keys = list(distribution.keys())
    probs = np.array([float(distribution[k]) for k in keys], dtype=float)
    total = probs.sum()
    if total <= 0:
        return fallback
    probs = probs / total
    return keys[int(rng.choice(len(keys), p=probs))]


def _normalize_field_type(field: str, value: Any) -> Any:
    if field in BOOL_FIELDS:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "1", "yes"}:
                return True
            if lowered in {"false", "0", "no"}:
                return False
        return bool(value)
    if field in INT_FIELDS:
        return int(value)
    if field in FLOAT_FIELDS:
        return float(value)
    if field in STRING_FIELDS:
        return str(value)
    return value


def sample_parameters(mode: str, config: dict[str, Any] | None, template_data: dict[str, Any] | None = None, sample_index: int = 0) -> dict[str, Any]:
    merged = deepcopy(DEFAULTS)

    template_defaults = deepcopy((template_data or {}).get("default_parameters", {}))
    if template_defaults:
        merged.update(template_defaults)

    incoming = deepcopy(config or {})
    template_defaults_applied = bool(incoming.pop("template_defaults_applied", False))
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
    enforced_fields: dict[str, Any] = {}
    if mode == "probabilistic":
        distributions = deepcopy((template_data or {}).get("probability_distributions", {}))
        base_seed = int(merged.get("seed", DEFAULTS["seed"]))
        rng = np.random.default_rng(base_seed + sample_index)
        for field in SUPPORTED_PROB_FIELDS:
            sampled_value = _choice_by_distribution(rng, distributions.get(field), merged.get(field))
            normalized_value = _normalize_field_type(field, sampled_value)
            sampled_parameters[field] = normalized_value
            merged[field] = normalized_value
            enforced_fields[field] = normalized_value

    merged = _validate_common(merged)
    merged["mode"] = mode
    merged["sampled_parameters"] = sampled_parameters
    merged["template_enforced_fields"] = enforced_fields
    merged["template_defaults_applied"] = template_defaults_applied
    merged["actual_parameters"] = {key: merged[key] for key in TRACKED_ACTUAL_FIELDS if key in merged}
    return merged
