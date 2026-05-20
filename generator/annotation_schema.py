"""MCG-JSON schema constructor for V0."""

from __future__ import annotations

from typing import Any


def build_mcg_json(
    dataset_info: dict[str, Any],
    image: dict[str, Any],
    plot_area: dict[str, Any],
    axis: dict[str, Any],
    style: dict[str, Any],
    legend: dict[str, Any],
    curves: list[dict[str, Any]],
    quality_check: dict[str, Any],
) -> dict[str, Any]:
    return {
        "dataset_info": dataset_info,
        "image": image,
        "plot_area": plot_area,
        "axis": axis,
        "style": style,
        "legend": legend,
        "curves": curves,
        "quality_check": quality_check,
    }
