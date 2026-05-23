from __future__ import annotations

from pathlib import Path
from typing import Any
from datetime import datetime
from uuid import uuid4

import numpy as np
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from generator.annotation_exporter import export_curve_csv, export_mcg_json
from generator.annotation_schema import build_mcg_json
from generator.curve_models import generate_curve_data
from generator.quality_check import run_quality_check
from generator.renderer import render_preview
from generator.sampler import sample_parameters
from generator.dataset_generator import generate_dataset

app = FastAPI(title="Materials Curve Dataset Platform API", version="0.4.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_DIR = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = ROOT_DIR / "templates"
EXAMPLES_PREVIEW_DIR = ROOT_DIR / "examples" / "previews"

# Ensure runtime directories always exist so startup and generation do not fail.
for path in [
    ROOT_DIR / "examples",
    EXAMPLES_PREVIEW_DIR / "images",
    EXAMPLES_PREVIEW_DIR / "csv",
    EXAMPLES_PREVIEW_DIR / "annotations",
    ROOT_DIR / "datasets",
]:
    path.mkdir(parents=True, exist_ok=True)

app.mount("/examples", StaticFiles(directory=ROOT_DIR / "examples"), name="examples")



class GenerateRequest(BaseModel):
    dataset_name: str = "creep_synth"
    version: str = "v0.1"
    total_count: int = 30
    mode: str = "explicit"
    template_id: str = "real_mainstream"
    seed: int = 20260520

    split: dict[str, float] = Field(default_factory=lambda: {"train": 0.7, "val": 0.2, "test": 0.1})

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


class PreviewRequest(BaseModel):
    mode: str = "explicit"
    template_id: str = "real_mainstream"

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


def _load_template(template_id: str) -> dict[str, Any]:
    template_path = TEMPLATES_DIR / f"{template_id}.yaml"
    if not template_path.exists():
        raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")

    try:
        data = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise HTTPException(status_code=400, detail=f"Template YAML format error: {template_path.name}: {exc}") from exc

    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail=f"Template format must be object: {template_path.name}")
    return data


@app.get('/health')
def health() -> dict[str, str]:
    return {"status": "ok", "service": "materials-curve-backend"}


@app.get('/templates')
def list_templates() -> dict[str, Any]:
    if not TEMPLATES_DIR.exists():
        raise HTTPException(status_code=500, detail="Templates directory is missing")

    items: list[dict[str, str]] = []
    for path in sorted(TEMPLATES_DIR.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("YAML root must be object")
            template_id = path.stem
            items.append(
                {
                    "template_id": template_id,
                    "template_name": str(data.get("template_name", template_id)),
                    "description": str(data.get("description", "")),
                    "file_name": path.name,
                }
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid template file {path.name}: {exc}") from exc

    return {"status": "ok", "count": len(items), "items": items}


@app.post('/preview')
def preview(req: PreviewRequest) -> dict[str, Any]:
    if req.mode not in {"explicit", "probabilistic"}:
        raise HTTPException(status_code=400, detail="mode must be explicit or probabilistic")

    template_data = _load_template(req.template_id)
    params_base = req.model_dump()
    root = ROOT_DIR
    base = root / "examples" / "previews"
    images_dir = base / "images"
    csv_dir = base / "csv"
    ann_dir = base / "annotations"
    for d in (images_dir, csv_dir, ann_dir):
        d.mkdir(parents=True, exist_ok=True)

    preview_run_id = f"preview_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}"
    items = []
    for i in range(max(3, min(req.preview_count, 6))):
        params = sample_parameters(req.mode, params_base, template_data=template_data, sample_index=i)
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
            csv_path = csv_dir / f"{preview_run_id}_{i+1}_curve_{curve_idx+1}.csv"
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
        image_path = images_dir / f"{preview_run_id}_{i+1}.png"
        render_info = render_preview(sample, image_path)

        for idx, curve in enumerate(curves):
            curve["pixel_points"] = render_info["curve_pixel_points"][idx]
            curve["bbox_xyxy"] = render_info["curve_bbox_xyxy"][idx]
            curve["line_color"] = curve.get("line_color", "#1f77b4")

        annotation = build_mcg_json(
            {
                "dataset_info": {
                    "name": "preview",
                    "version": "v0-step4",
                    "mode": params["mode"],
                    "template_id": req.template_id,
                    "template_name": template_data.get("template_name", req.template_id),
                    "seed": params["seed"],
                },
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
                    "mode": params["mode"],
                    "template_id": req.template_id,
                    "template_name": template_data.get("template_name", req.template_id),
                    "sampled_parameters": params.get("sampled_parameters", {}),
                    "actual_parameters": params.get("actual_parameters", {}),
                },
                "legend": {"position": params["legend_position"]},
                "curves": curves,
                "quality_check": {},
            }
        )
        annotation["quality_check"] = run_quality_check(annotation)

        ann_path = ann_dir / f"{preview_run_id}_{i+1}.json"
        export_mcg_json(annotation, ann_path)

        items.append(
            {
                "image_path": str(image_path.relative_to(root)),
                "annotation_path": str(ann_path.relative_to(root)),
                "csv_paths": csv_paths,
                "annotation": annotation,
            }
        )

    return {"status": "ok", "preview_run_id": preview_run_id, "preview_count": len(items), "items": items}


@app.post('/generate')
def generate(req: GenerateRequest) -> dict[str, Any]:
    if req.mode not in {"explicit", "probabilistic"}:
        raise HTTPException(status_code=400, detail="mode must be explicit or probabilistic")

    if req.total_count <= 0:
        raise HTTPException(status_code=400, detail="total_count must be positive")

    split_total = req.split.get("train", 0) + req.split.get("val", 0) + req.split.get("test", 0)
    if abs(split_total - 1.0) > 1e-6:
        raise HTTPException(status_code=400, detail="split ratios must sum to 1.0")

    template_data = _load_template(req.template_id)
    result = generate_dataset(ROOT_DIR, req.model_dump(), template_data)
    return {
        "status": "ok",
        "dataset_id": result.dataset_id,
        "dataset_path": result.dataset_path,
        "total_count": result.total_count,
        "split_counts": result.split_counts,
        "summary_path": result.summary_path,
        "quality_report_path": result.quality_report_path,
    }
