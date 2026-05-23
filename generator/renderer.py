"""Matplotlib renderer for preview curve charts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


BW_PALETTE=["#111111", "#444444", "#666666", "#888888", "#222222"]
MARKER_MAP = {
    "triangle": "^",
    "circle": "o",
    "square": "s",
}


def _legend_loc(position: str) -> str:
    mapping = {
        "inside_upper_right": "upper right",
        "inside_upper_left": "upper left",
        "inside_lower_right": "lower right",
    }
    return mapping.get(position, "upper right")


def render_preview(sample: dict[str, Any], image_path: Path) -> dict[str, Any]:
    """Render chart and return image/plot/curve pixel metadata."""
    fig, ax = plt.subplots(figsize=(8, 5), dpi=120)
    ax.set_title(sample["title"])
    x_unit = "" if sample["x_unit"] == "none" else sample["x_unit"]
    y_unit = "" if sample["y_unit"] == "none" else sample["y_unit"]
    ax.set_xlabel(f"{sample['x_label']}" if not x_unit else f"{sample['x_label']} ({x_unit})")
    ax.set_ylabel(f"{sample['y_label']}" if not y_unit else f"{sample['y_label']} ({y_unit})")
    ax.grid(bool(sample["grid"]))

    curve_pixels: list[list[list[float]]] = []
    curve_bboxes: list[list[float]] = []

    for idx, curve in enumerate(sample["curves"]):
        data_points = curve["data_points"]
        x = [p[0] for p in data_points]
        y = [p[1] for p in data_points]
        marker_key = sample["marker"]
        marker = None if marker_key == "none" else MARKER_MAP.get(marker_key, marker_key)
        markevery = None if marker is None else max(8, min(20, int(len(x) / 10)))
        color = None
        if sample.get("template_id") == "black_white_paper":
            color = BW_PALETTE[idx % len(BW_PALETTE)]
        line, = ax.plot(
            x,
            y,
            linestyle=sample["line_style"],
            marker=marker,
            markevery=markevery,
            linewidth=sample["line_width"],
            label=f"Curve {idx+1}",
            color=color,
        )
        disp = ax.transData.transform(list(zip(x, y)))
        pixels = [[float(px), float(py)] for px, py in disp]
        curve_pixels.append(pixels)
        xs = [p[0] for p in pixels]
        ys = [p[1] for p in pixels]
        curve_bboxes.append([min(xs), min(ys), max(xs), max(ys)])
        curve["line_color"] = line.get_color()

    if sample["legend_position"] != "none":
        if sample["legend_position"] == "outside_right":
            ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), borderaxespad=0.0)
            fig.tight_layout(rect=(0, 0, 0.86, 1))
        else:
            ax.legend(loc=_legend_loc(sample["legend_position"]))
            fig.tight_layout()
    else:
        fig.tight_layout()
    fig.canvas.draw()

    renderer = fig.canvas.get_renderer()
    plot_bb = ax.get_window_extent(renderer=renderer)
    width, height = fig.canvas.get_width_height()

    image_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(image_path, format="png")
    plt.close(fig)

    return {
        "image_path": str(image_path),
        "image_width": int(width),
        "image_height": int(height),
        "plot_area_bbox_xyxy": [float(plot_bb.x0), float(plot_bb.y0), float(plot_bb.x1), float(plot_bb.y1)],
        "curve_pixel_points": curve_pixels,
        "curve_bbox_xyxy": curve_bboxes,
    }
