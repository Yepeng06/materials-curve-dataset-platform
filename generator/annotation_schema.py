"""MCG-JSON schema builder for preview samples."""

from __future__ import annotations

from typing import Any


def build_mcg_json(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "dataset_info": payload["dataset_info"],
        "image": payload["image"],
        "plot_area": payload["plot_area"],
        "axis": payload["axis"],
        "style": payload["style"],
        "legend": payload["legend"],
        "curves": payload["curves"],
        "quality_check": payload["quality_check"],
    }
