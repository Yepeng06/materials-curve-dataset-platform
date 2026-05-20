"""Style model placeholders for V0."""

from dataclasses import dataclass


@dataclass
class CurveStyle:
    line_style: str = "solid"
    line_width: float = 1.5
    marker: str = "none"
