"""Export helpers for preview artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def export_curve_csv(data_points: list[list[float]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y"])
        writer.writerows(data_points)


def export_mcg_json(annotation: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(annotation, ensure_ascii=False, indent=2), encoding="utf-8")
