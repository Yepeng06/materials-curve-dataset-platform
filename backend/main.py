from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from generator.annotation_exporter import export_curve_csv, export_mcg_json
from generator.annotation_schema import build_mcg_json
from generator.curve_models import generate_multi_curves
from generator.quality_check import run_quality_check
from generator.renderer import render_preview
from generator.sampler import sample_parameters

app = FastAPI(title="Materials Curve Dataset Platform API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
PREVIEW_ROOT = BASE_DIR / "examples" / "previews"
IMAGES_DIR = PREVIEW_ROOT / "images"
CSV_DIR = PREVIEW_ROOT / "csv"
ANNOTATIONS_DIR = PREVIEW_ROOT / "annotations"

app.mount("/examples", StaticFiles(directory=str(BASE_DIR / "examples")), name="examples")


class PreviewRequest(BaseModel):
    preview_count: int = 3
    num_curves: int = 3
    curve_shape: str = "near_linear"
    x_label: str = "Creep time"
    x_unit: str = "h"
    y_label: str = "Creep strain"
    y_unit: str = "%"
    x_range: list[float] = [0, 1000]
    y_range: list[float] | None = None
    line_style: str = "solid"
    marker: str = "none"
    legend_position: str = "inside_upper_right"
    grid: bool = False
    seed: int = 20260520


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "materials-curve-backend"}


@app.post("/preview")
def preview(payload: PreviewRequest) -> dict[str, Any]:
    params = sample_parameters("explicit", payload.model_dump())
    preview_count = params["preview_count"]

    items: list[dict[str, Any]] = []
    for idx in range(preview_count):
        sample_id = f"preview_{idx + 1:03d}"
        seed_for_item = params["seed"] + idx
        curves = generate_multi_curves(
            shape=params["curve_shape"],
            num_curves=params["num_curves"],
            point_count=params.get("point_count", 120),
            x_range=(float(params["x_range"][0]), float(params["x_range"][1])),
            seed=seed_for_item,
        )

        image_path = IMAGES_DIR / f"{sample_id}.png"
        render_result = render_preview(curves, params, image_path)

        csv_paths: list[str] = []
        for curve in render_result["curves"]:
            csv_path = CSV_DIR / f"{sample_id}_{curve['curve_id']}.csv"
            curve["csv_path"] = export_curve_csv(curve["data_points"], csv_path)
            csv_paths.append(curve["csv_path"])

        qc = run_quality_check(render_result["curves"], render_result["plot_area_bbox"])
        created_at = datetime.now(UTC).isoformat()
        annotation = build_mcg_json(
            dataset_info={
                "dataset_id": "preview_v0",
                "sample_id": sample_id,
                "generator_version": "0.2.0",
                "seed": seed_for_item,
                "created_at": created_at,
            },
            image={
                "file_name": image_path.name,
                "file_path": str(image_path),
                "width": render_result["width"],
                "height": render_result["height"],
            },
            plot_area={"bbox_xyxy": render_result["plot_area_bbox"]},
            axis={
                "x": {"label": params["x_label"], "unit": params["x_unit"], "range": params["x_range"]},
                "y": {"label": params["y_label"], "unit": params["y_unit"], "range": params["y_range"]},
            },
            style={
                "template": "real_mainstream",
                "num_curves": params["num_curves"],
                "line_style": params["line_style"],
                "marker": params["marker"],
                "legend_position": params["legend_position"],
                "grid": params["grid"],
                "curve_shape": params["curve_shape"],
            },
            legend={"visible": True, "position": params["legend_position"]},
            curves=render_result["curves"],
            quality_check=qc,
        )

        annotation_path = ANNOTATIONS_DIR / f"{sample_id}.json"
        annotation_saved = export_mcg_json(annotation, annotation_path)
        items.append(
            {
                "image_path": f"/examples/previews/images/{image_path.name}",
                "annotation_path": annotation_saved,
                "csv_paths": csv_paths,
                "annotation": annotation,
            }
        )

    return {"status": "ok", "preview_count": preview_count, "items": items}
