"""Basic quality checks for generated preview samples."""

from __future__ import annotations

import math
from typing import Any


def run_quality_check(annotation: dict[str, Any]) -> dict[str, Any]:
    warnings: list[str] = []
    passed = True
    plot = annotation["plot_area"]["bbox_xyxy"]

    for curve in annotation["curves"]:
        data_points = curve.get("data_points", [])
        pixel_points = curve.get("pixel_points", [])
        bbox = curve.get("bbox_xyxy", [])

        if not data_points:
            passed = False
            warnings.append(f"{curve['curve_id']}: empty data_points")
        if not pixel_points:
            passed = False
            warnings.append(f"{curve['curve_id']}: empty pixel_points")
        if len(data_points) != len(pixel_points):
            passed = False
            warnings.append(f"{curve['curve_id']}: points length mismatch")
        if len(bbox) != 4:
            passed = False
            warnings.append(f"{curve['curve_id']}: invalid bbox")

        for pt in data_points + pixel_points:
            if any((not math.isfinite(v)) for v in pt):
                passed = False
                warnings.append(f"{curve['curve_id']}: NaN/inf detected")
                break

        if len(bbox) == 4:
            if bbox[0] < plot[0] - 20 or bbox[1] < plot[1] - 20 or bbox[2] > plot[2] + 20 or bbox[3] > plot[3] + 20:
                warnings.append(f"{curve['curve_id']}: curve bbox exceeds plot area")

    return {"passed": passed, "warnings": warnings}
