"""Curve data model skeletons for V0."""

from typing import List, Tuple


Point = Tuple[float, float]


def near_linear_curve() -> List[Point]:
    """Return a tiny placeholder near-linear curve for V0 scaffolding."""
    return [(0.0, 0.1), (10.0, 0.2), (20.0, 0.3)]
