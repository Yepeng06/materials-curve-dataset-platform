"""Annotation exporter placeholder for V0."""

from pathlib import Path
from typing import Any
import json


def export_mcg_json(annotation: dict[str, Any], output_path: Path) -> None:
    """Write MCG-JSON annotation to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(annotation, ensure_ascii=False, indent=2), encoding="utf-8")
