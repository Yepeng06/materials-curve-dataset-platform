"""Sampling mode placeholders for V0."""

from typing import Any


def sample_parameters(mode: str, config: dict[str, Any]) -> dict[str, Any]:
    """Return explicit config in V0; probabilistic mode to be added later."""
    if mode == "explicit":
        return config
    return config
