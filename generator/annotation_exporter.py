"""Export PNG/CSV/MCG-JSON assets for V0 preview."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def export_curve_csv(data_points: list[list[float]], output_path: Path) -> str:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y"])
        writer.writerows(data_points)
    return str(output_path)


def export_mcg_json(annotation: dict[str, Any], output_path: Path) -> str:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(annotation, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(output_path)
