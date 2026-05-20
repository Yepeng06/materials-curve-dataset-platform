"""Basic quality checks for V0 preview annotations."""

from __future__ import annotations

import math
from typing import Any


def _is_finite_points(points: list[list[float]]) -> bool:
    return all(math.isfinite(p[0]) and math.isfinite(p[1]) for p in points)


def run_quality_check(curves: list[dict[str, Any]], plot_area_bbox: list[float]) -> dict[str, Any]:
    warnings: list[str] = []
    px0, py0, px1, py1 = plot_area_bbox

    for curve in curves:
        cid = curve.get("curve_id", "unknown")
        data_points = curve.get("data_points", [])
        pixel_points = curve.get("pixel_points", [])
        bbox = curve.get("bbox_xyxy", [])

        if not data_points:
            warnings.append(f"{cid}: empty data_points")
        if not pixel_points:
            warnings.append(f"{cid}: empty pixel_points")
        if len(data_points) != len(pixel_points):
            warnings.append(f"{cid}: data_points and pixel_points length mismatch")
        if len(bbox) != 4 or bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
            warnings.append(f"{cid}: invalid bbox")
        if not _is_finite_points(data_points):
            warnings.append(f"{cid}: data_points contains NaN or inf")
        if not _is_finite_points(pixel_points):
            warnings.append(f"{cid}: pixel_points contains NaN or inf")

        if pixel_points:
            for xp, yp in pixel_points:
                if xp < px0 - 5 or xp > px1 + 5 or yp < py0 - 5 or yp > py1 + 5:
                    warnings.append(f"{cid}: some pixel_points are outside plot area")
                    break

    return {"passed": len(warnings) == 0, "warnings": warnings}
