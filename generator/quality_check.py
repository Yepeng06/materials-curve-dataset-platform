"""Quality check placeholder for V0."""

from typing import Any


def run_quality_check(annotation: dict[str, Any]) -> dict[str, Any]:
    """Return a minimal pass status for V0."""
    _ = annotation
    return {"passed": True, "warnings": ["V0 placeholder check only"]}
