"""Renderer placeholder for V0."""

from typing import Any


def render_preview(sample: dict[str, Any]) -> dict[str, Any]:
    """Return placeholder render metadata for V0 scaffolding."""
    return {
        "image_path": "examples/preview_placeholder.png",
        "plot_area_bbox": [120, 80, 900, 650],
        "pixel_points": [],
    }
