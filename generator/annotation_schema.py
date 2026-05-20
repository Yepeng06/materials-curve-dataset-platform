"""MCG-JSON schema helpers for V0."""

from typing import Any


def build_mcg_json() -> dict[str, Any]:
    """Return a minimal MCG-JSON placeholder."""
    return {
        "dataset_info": {},
        "image": {},
        "plot_area": {},
        "axis": {},
        "style": {},
        "legend": {},
        "curves": [],
        "quality_check": {},
    }
