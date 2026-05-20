from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from generator.annotation_exporter import export_curve_csv, export_mcg_json
from generator.annotation_schema import build_mcg_json
from generator.curve_models import generate_curve_data
from generator.quality_check import run_quality_check
from generator.renderer import render_preview
from generator.sampler import sample_parameters

app = FastAPI(title="Materials Curve Dataset Platform API", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_DIR = Path(__file__).resolve().parents[1]
app.mount("/examples", StaticFiles(directory=ROOT_DIR / "examples"), name="examples")


class PreviewRequest(BaseModel):
    preview_count: int = 3
    seed: int = 20260520
    grid: bool = False

    x_label: str = "Creep time"
    x_unit: str = "h"
    y_label: str = "Creep strain"
    y_unit: str = "%"

    num_curves: int = 3
    curve_shape: str = "near_linear"
    points_per_curve: int = 160
    noise_level: float = 0.02

    line_style: str = "solid"
    line_width: float = 1.5
    marker: str = "none"

    legend_position: str = "inside_upper_right"
    x_range: list[float] = Field(default_factory=lambda: [0, 1000])


@app.get('/health')
def health() -> dict[str, str]:
    return {"status": "ok", "service": "materials-curve-backend"}


@app.post('/preview')
def preview(req: PreviewRequest) -> dict[str, Any]:
    params = sample_parameters("explicit", req.model_dump())
    root = ROOT_DIR
    base = root / "examples" / "previews"
    images_dir = base / "images"
    csv_dir = base / "csv"
    ann_dir = base / "annotations"

    items = []
    for i in range(params["preview_count"]):
        rng = np.random.default_rng(params["seed"] + i)
        curves = []
        csv_paths = []

        for curve_idx in range(params["num_curves"]):
            data_points = generate_curve_data(
                curve_shape=params["curve_shape"],
                x_min=float(params["x_range"][0]),
                x_max=float(params["x_range"][1]),
                num_points=params["points_per_curve"],
                noise_level=params["noise_level"],
                rng=rng,
            )
            csv_path = csv_dir / f"preview_{i+1}_curve_{curve_idx+1}.csv"
            export_curve_csv(data_points, csv_path)
            csv_paths.append(str(csv_path.relative_to(root)))
            curves.append(
                {
                    "curve_id": f"curve_{curve_idx+1}",
                    "label": f"Curve {curve_idx+1}",
                    "shape_type": params["curve_shape"],
                    "line_style": params["line_style"],
                    "line_width": params["line_width"],
                    "marker": params["marker"],
                    "data_points": data_points,
                    "csv_path": str(csv_path.relative_to(root)),
                }
            )

        sample = dict(params)
        sample["curves"] = curves
        image_path = images_dir / f"preview_{i+1}.png"
        render_info = render_preview(sample, image_path)

        for idx, curve in enumerate(curves):
            curve["pixel_points"] = render_info["curve_pixel_points"][idx]
            curve["bbox_xyxy"] = render_info["curve_bbox_xyxy"][idx]
            curve["line_color"] = curve.get("line_color", "#1f77b4")

        annotation = build_mcg_json(
            {
                "dataset_info": {"name": "preview", "version": "v0-step3"},
                "image": {
                    "image_path": str(image_path.relative_to(root)),
                    "width": render_info["image_width"],
                    "height": render_info["image_height"],
                },
                "plot_area": {"bbox_xyxy": render_info["plot_area_bbox_xyxy"]},
                "axis": {
                    "x_label": params["x_label"], "x_unit": params["x_unit"],
                    "y_label": params["y_label"], "y_unit": params["y_unit"],
                    "x_range": params["x_range"],
                },
                "style": {
                    "grid": params["grid"],
                    "line_style": params["line_style"],
                    "line_width": params["line_width"],
                    "marker": params["marker"],
                    "legend_position": params["legend_position"],
                    "curve_shape": params["curve_shape"],
                    "points_per_curve": params["points_per_curve"],
                    "noise_level": params["noise_level"],
                    "seed": params["seed"],
                },
                "legend": {"position": params["legend_position"]},
                "curves": curves,
                "quality_check": {},
            }
        )
        annotation["quality_check"] = run_quality_check(annotation)

        ann_path = ann_dir / f"preview_{i+1}.json"
        export_mcg_json(annotation, ann_path)

        items.append(
            {
                "image_path": str(image_path.relative_to(root)),
                "annotation_path": str(ann_path.relative_to(root)),
                "csv_paths": csv_paths,
                "annotation": annotation,
            }
        )

    return {"status": "ok", "preview_count": len(items), "items": items}
