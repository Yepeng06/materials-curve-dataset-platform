"""Matplotlib renderer for V0 preview generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]


def _legend_loc(position: str) -> str:
    mapping = {
        "inside_upper_right": "upper right",
        "inside_upper_left": "upper left",
        "inside_lower_right": "lower right",
        "inside_lower_left": "lower left",
    }
    return mapping.get(position, "upper right")


def render_preview(
    curves_data: list[list[list[float]]],
    sample: dict[str, Any],
    image_path: Path,
) -> dict[str, Any]:
    image_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
    ax.set_title(sample.get("title", "Synthetic Steel Creep Curves"))
    ax.set_xlabel(f"{sample['x_label']} ({sample['x_unit']})")
    ax.set_ylabel(f"{sample['y_label']} ({sample['y_unit']})")
    ax.grid(bool(sample.get("grid", False)))

    x_min, x_max = sample["x_range"]
    ax.set_xlim(float(x_min), float(x_max))

    curve_infos: list[dict[str, Any]] = []
    all_y: list[float] = []
    for idx, points in enumerate(curves_data):
        arr = np.array(points, dtype=float)
        x = arr[:, 0]
        y = arr[:, 1]
        all_y.extend(y.tolist())
        label = f"Curve {idx + 1}"
        line_color = COLORS[idx % len(COLORS)]
        line, = ax.plot(
            x,
            y,
            label=label,
            linestyle=sample["line_style"],
            marker=None if sample["marker"] == "none" else sample["marker"],
            linewidth=1.8,
            color=line_color,
        )

        pixel_points = ax.transData.transform(np.column_stack([x, y]))
        xpix = pixel_points[:, 0]
        ypix = pixel_points[:, 1]
        curve_infos.append(
            {
                "curve_id": f"curve_{idx + 1}",
                "label": label,
                "shape_type": sample["curve_shape"],
                "line_color": line_color,
                "line_style": line.get_linestyle(),
                "line_width": float(line.get_linewidth()),
                "marker": sample["marker"],
                "data_points": [[float(a), float(b)] for a, b in zip(x, y, strict=True)],
                "pixel_points": [[float(a), float(b)] for a, b in zip(xpix, ypix, strict=True)],
                "bbox_xyxy": [float(xpix.min()), float(ypix.min()), float(xpix.max()), float(ypix.max())],
            }
        )

    if all_y:
        y_max = max(all_y) * 1.15
        ax.set_ylim(0.0, y_max)

    ax.legend(loc=_legend_loc(sample["legend_position"]))
    fig.canvas.draw()

    plot_bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    plot_area_pixels = [
        float(plot_bbox.x0 * fig.dpi),
        float(plot_bbox.y0 * fig.dpi),
        float(plot_bbox.x1 * fig.dpi),
        float(plot_bbox.y1 * fig.dpi),
    ]

    fig.savefig(image_path, format="png", bbox_inches="tight")
    width, height = fig.canvas.get_width_height()
    plt.close(fig)

    return {
        "image_path": str(image_path),
        "width": int(width),
        "height": int(height),
        "plot_area_bbox": plot_area_pixels,
        "curves": curve_infos,
    }
