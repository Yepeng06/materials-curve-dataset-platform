from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from generator.annotation_exporter import export_curve_csv, export_mcg_json
from generator.annotation_schema import build_mcg_json
from generator.curve_models import generate_curve_data
from generator.quality_check import run_quality_check
from generator.renderer import render_preview
from generator.sampler import sample_parameters


@dataclass
class GenerateResult:
    dataset_id: str
    dataset_path: str
    total_count: int
    split_counts: dict[str, int]
    summary_path: str
    quality_report_path: str


def _split_counts(total_count: int, split: dict[str, float]) -> dict[str, int]:
    ordered = ["train", "val", "test"]
    raw = {k: total_count * float(split.get(k, 0.0)) for k in ordered}
    counts = {k: int(raw[k]) for k in ordered}
    assigned = sum(counts.values())
    remains = sorted(ordered, key=lambda k: raw[k] - counts[k], reverse=True)
    idx = 0
    while assigned < total_count:
        counts[remains[idx % len(remains)]] += 1
        assigned += 1
        idx += 1
    return counts


def _build_dataset_id(root: Path, dataset_name: str, version: str) -> str:
    date_part = datetime.utcnow().strftime("%Y%m%d")
    prefix = f"{dataset_name}_{version}_{date_part}_"
    existing = [p.name for p in (root / "datasets").glob(f"{prefix}*") if p.is_dir()]
    seq = 1
    if existing:
        seq = max(int(name.rsplit("_", 1)[-1]) for name in existing if name.rsplit("_", 1)[-1].isdigit()) + 1
    return f"{prefix}{seq:03d}"


def generate_dataset(root: Path, req_data: dict[str, Any], template_data: dict[str, Any]) -> GenerateResult:
    dataset_id = _build_dataset_id(root, req_data["dataset_name"], req_data["version"])
    dataset_dir = root / "datasets" / dataset_id
    split = req_data["split"]
    counts = _split_counts(int(req_data["total_count"]), split)
    assignments: list[str] = [
        *(["train"] * counts["train"]),
        *(["val"] * counts["val"]),
        *(["test"] * counts["test"]),
    ]

    for bucket in ["images", "annotations", "csv"]:
        for part in ["train", "val", "test"]:
            (dataset_dir / bucket / part).mkdir(parents=True, exist_ok=True)

    global_seed = int(req_data.get("seed", 20260520))
    mode = req_data["mode"]
    base_params = dict(req_data)

    num_curves_stats: Counter[str] = Counter()
    curve_shape_stats: Counter[str] = Counter()
    line_style_stats: Counter[str] = Counter()
    marker_stats: Counter[str] = Counter()
    legend_stats: Counter[str] = Counter()
    grid_stats: Counter[str] = Counter()

    sample_seeds: dict[str, int] = {}
    warnings_by_sample: dict[str, list[str]] = {}
    passed_count = 0
    warning_count = 0
    failed_count = 0

    for i in range(int(req_data["total_count"])):
        sample_id = f"creep_{i + 1:06d}"
        split_name = assignments[i]
        sample_seed = global_seed + i
        sample_seeds[sample_id] = sample_seed

        params = sample_parameters(mode, {**base_params, "seed": sample_seed}, template_data=template_data, sample_index=i)
        rng = np.random.default_rng(sample_seed)
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
            csv_rel = Path("csv") / split_name / f"{sample_id}_curve_{curve_idx + 1}.csv"
            export_curve_csv(data_points, dataset_dir / csv_rel)
            csv_paths.append(str(csv_rel))
            curves.append(
                {
                    "curve_id": f"curve_{curve_idx + 1}",
                    "label": f"Curve {curve_idx + 1}",
                    "shape_type": params["curve_shape"],
                    "line_style": params["line_style"],
                    "line_width": params["line_width"],
                    "marker": params["marker"],
                    "data_points": data_points,
                    "csv_path": str(csv_rel),
                }
            )

        sample = dict(params)
        sample["curves"] = curves
        image_rel = Path("images") / split_name / f"{sample_id}.png"
        render_info = render_preview(sample, dataset_dir / image_rel)

        for idx, curve in enumerate(curves):
            curve["pixel_points"] = render_info["curve_pixel_points"][idx]
            curve["bbox_xyxy"] = render_info["curve_bbox_xyxy"][idx]
            curve["line_color"] = curve.get("line_color", "#1f77b4")

        ann_rel = Path("annotations") / split_name / f"{sample_id}.json"
        annotation = build_mcg_json(
            {
                "dataset_info": {
                    "name": req_data["dataset_name"],
                    "version": req_data["version"],
                    "dataset_id": dataset_id,
                    "mode": mode,
                    "template_id": req_data["template_id"],
                    "template_name": template_data.get("template_name", req_data["template_id"]),
                    "seed": global_seed,
                },
                "image": {
                    "image_path": str(image_rel),
                    "annotation_path": str(ann_rel),
                    "csv_paths": csv_paths,
                    "width": render_info["image_width"],
                    "height": render_info["image_height"],
                    "sample_id": sample_id,
                    "split": split_name,
                    "mode": mode,
                    "template_id": req_data["template_id"],
                    "template_name": template_data.get("template_name", req_data["template_id"]),
                    "seed": global_seed,
                    "sample_seed": sample_seed,
                    "actual_parameters": params.get("actual_parameters", {}),
                },
                "plot_area": {"bbox_xyxy": render_info["plot_area_bbox_xyxy"]},
                "axis": {
                    "x_label": params["x_label"],
                    "x_unit": params["x_unit"],
                    "y_label": params["y_label"],
                    "y_unit": params["y_unit"],
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
                    "seed": sample_seed,
                    "mode": mode,
                    "template_id": req_data["template_id"],
                    "template_name": template_data.get("template_name", req_data["template_id"]),
                    "sampled_parameters": params.get("sampled_parameters", {}),
                    "actual_parameters": params.get("actual_parameters", {}),
                },
                "legend": {"position": params["legend_position"]},
                "curves": curves,
                "quality_check": {},
            }
        )
        quality = run_quality_check(annotation)
        annotation["quality_check"] = quality
        export_mcg_json(annotation, dataset_dir / ann_rel)

        if quality["passed"]:
            passed_count += 1
        else:
            failed_count += 1
        if quality["warnings"]:
            warning_count += 1
            warnings_by_sample[sample_id] = quality["warnings"]

        num_curves_stats[str(params["num_curves"])] += 1
        curve_shape_stats[str(params["curve_shape"])] += 1
        line_style_stats[str(params["line_style"])] += 1
        marker_stats[str(params["marker"])] += 1
        legend_stats[str(params["legend_position"])] += 1
        grid_stats[str(params["grid"])] += 1

    config_path = dataset_dir / "config.yaml"
    config_path.write_text(yaml.safe_dump(req_data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    distribution_payload: dict[str, Any] = {
        "mode": mode,
        "template_id": req_data["template_id"],
        "probability_distributions": template_data.get("probability_distributions", {}),
    }
    (dataset_dir / "distribution.yaml").write_text(
        yaml.safe_dump(distribution_payload, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

    (dataset_dir / "seed.json").write_text(
        json.dumps({"global_seed": global_seed, "sample_seeds": sample_seeds}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary = {
        "dataset_id": dataset_id,
        "total_count": int(req_data["total_count"]),
        "split_counts": counts,
        "mode": mode,
        "template_id": req_data["template_id"],
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "num_curves_distribution": dict(num_curves_stats),
        "curve_shape_distribution": dict(curve_shape_stats),
        "line_style_distribution": dict(line_style_stats),
        "marker_distribution": dict(marker_stats),
        "legend_position_distribution": dict(legend_stats),
        "grid_distribution": dict(grid_stats),
    }
    (dataset_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    quality_report = {
        "total_count": int(req_data["total_count"]),
        "passed_count": passed_count,
        "warning_count": warning_count,
        "failed_count": failed_count,
        "warnings_by_sample": warnings_by_sample,
    }
    (dataset_dir / "quality_report.json").write_text(
        json.dumps(quality_report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    (dataset_dir / "README.md").write_text(
        "\n".join(
            [
                f"# Dataset {dataset_id}",
                "",
                f"- 数据集名称: {req_data['dataset_name']}",
                f"- 版本: {req_data['version']}",
                f"- 生成时间(UTC): {summary['generated_at']}",
                f"- 生成数量: {req_data['total_count']}",
                f"- 模式: {mode}",
                f"- 模板: {req_data['template_id']}",
                f"- 随机种子: {global_seed}",
                "",
                "## 目录结构",
                "- images/train|val|test: 图片文件",
                "- annotations/train|val|test: MCG-JSON 标注",
                "- csv/train|val|test: 曲线 CSV",
                "- config.yaml: 请求配置",
                "- distribution.yaml: 模板概率分布",
                "- seed.json: 全局与样本种子",
                "- summary.json: 统计摘要",
                "- quality_report.json: 质量检查报告",
            ]
        ),
        encoding="utf-8",
    )

    return GenerateResult(
        dataset_id=dataset_id,
        dataset_path=str(Path("datasets") / dataset_id),
        total_count=int(req_data["total_count"]),
        split_counts=counts,
        summary_path=str(Path("datasets") / dataset_id / "summary.json"),
        quality_report_path=str(Path("datasets") / dataset_id / "quality_report.json"),
    )
