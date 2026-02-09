# helpers/color/color_types.py
# Lightweight immutable color value types used by helpers.color utilities.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ColorRGB:
    """
    Immutable 8-bit RGB color.

    Notes:
      - Channels are intended to be in [0..255].
      - Use helpers.color.color_utils.normalize_rgb() to clamp/sanitize inputs.
    """
    r: int
    g: int
    b: int
