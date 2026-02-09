# helpers/color/color_utils.py
# UI-agnostic color helpers: RGB<->HSV, blending, luminance heuristics, accent/variant generation, parsing.

from __future__ import annotations

"""
helpers.color_utils
-------------------

Small, UI-agnostic color helpers.

Scope:
- RGB <-> HSV conversion
- basic blending
- simple luminance estimate (for black/white foreground choice)
- accent generation (opposite hue variants)
- generating low/muted/high variants from a single anchor color
- parsing colors from common CLI/user formats

Non-goals:
- strict contrast compliance (WCAG); these helpers are aesthetic/pragmatic.
"""

import colorsys
from dataclasses import dataclass
from typing import Optional

from .color_types import ColorRGB
from helpers.math.basic import clamp01, clamp8, lerp


def normalize_rgb(c: ColorRGB) -> ColorRGB:
    """
    Clamp RGB channels to 0..255 and return a new ColorRGB.

    This function is intended for sanitizing user input and
    keeping domain state well-defined.
    """
    # Clamp each channel into uint8 range; always return a new immutable value.
    return ColorRGB(r=clamp8(c.r), g=clamp8(c.g), b=clamp8(c.b))


# ─────────────────────────────────────────────────────────────
# RGB <-> HSV
# HSV components are floats in [0..1]
# ─────────────────────────────────────────────────────────────


def rgb_to_hsv(c: ColorRGB) -> tuple[float, float, float]:
    """
    Convert RGB (0..255) to HSV (0..1 floats).

    Hue is in [0..1], not degrees.
    """
    r = clamp01(c.r / 255.0)
    g = clamp01(c.g / 255.0)
    b = clamp01(c.b / 255.0)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h, s, v


def hsv_to_rgb(h: float, s: float, v: float) -> ColorRGB:
    """
    Convert HSV (0..1 floats) to RGB (0..255 ints).

    Hue is in [0..1], not degrees.
    """
    h = clamp01(h)
    s = clamp01(s)
    v = clamp01(v)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return ColorRGB(r=clamp8(round(r * 255)), g=clamp8(round(g * 255)), b=clamp8(round(b * 255)))


# ─────────────────────────────────────────────────────────────
# Blending / luminance heuristics
# ─────────────────────────────────────────────────────────────


def blend_rgb(a: ColorRGB, b: ColorRGB, t: float) -> ColorRGB:
    """
    Linear blend between colors in RGB space.

    This is simple and fast, but not gamma-correct. That is intentional here.
    """
    t = clamp01(t)
    return ColorRGB(
        r=clamp8(round(lerp(a.r, b.r, t))),
        g=clamp8(round(lerp(a.g, b.g, t))),
        b=clamp8(round(lerp(a.b, b.b, t))),
    )


def relative_luminance(c: ColorRGB) -> float:
    """
    Approximate relative luminance in [0..1].

    This is a pragmatic heuristic; not a strict WCAG implementation.
    """
    r = clamp01(c.r / 255.0)
    g = clamp01(c.g / 255.0)
    b = clamp01(c.b / 255.0)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def auto_fg_color(bg: ColorRGB, *, threshold: float = 0.5) -> ColorRGB:
    """
    Pick black or white foreground based on background luminance.

    threshold:
      - higher => more likely to choose black
      - lower => more likely to choose white
    """
    lum = relative_luminance(bg)
    return ColorRGB(0, 0, 0) if lum > threshold else ColorRGB(255, 255, 255)


# ─────────────────────────────────────────────────────────────
# Color transforms / accents
# ─────────────────────────────────────────────────────────────


def opposite_hue_color(c: ColorRGB) -> ColorRGB:
    """
    Return a color with hue shifted by 180 degrees (0.5 in [0..1] hue space),
    keeping saturation and value the same.
    """
    h, s, v = rgb_to_hsv(c)
    h2 = (h + 0.5) % 1.0
    return hsv_to_rgb(h2, s, v)


def opposite_contrast_color(c: ColorRGB) -> ColorRGB:
    """
    Return a practical accent/contrast color:
      - rotate hue by 180 degrees
      - slightly adjust saturation/value to avoid muddy midtones
    """
    h, s, v = rgb_to_hsv(c)
    h2 = (h + 0.5) % 1.0
    s2 = clamp01(s * 0.85 + 0.15)
    v2 = clamp01(v * 0.85 + 0.15)
    return hsv_to_rgb(h2, s2, v2)


def inverted_rgb(c: ColorRGB) -> ColorRGB:
    """Simple RGB inversion (255 - channel)."""
    return ColorRGB(r=255 - clamp8(c.r), g=255 - clamp8(c.g), b=255 - clamp8(c.b))


def accent_low(c: ColorRGB) -> ColorRGB:
    """
    Return a muted accent derived from the anchor color.

    Intended for subtle UI accents (borders, inactive chips, etc.).
    """
    h, s, v = rgb_to_hsv(opposite_hue_color(c))
    return hsv_to_rgb(h, s * 0.45, v * 0.85)


def accent_strong(c: ColorRGB) -> ColorRGB:
    """
    Return a vivid accent derived from the anchor color.

    Intended for highlights/active states.
    """
    h, s, v = rgb_to_hsv(opposite_hue_color(c))
    return hsv_to_rgb(h, clamp01(s * 1.15), clamp01(v * 1.05))


# ─────────────────────────────────────────────────────────────
# Variants from anchor
# ─────────────────────────────────────────────────────────────


def variants_from_anchor(
    anchor: ColorRGB,
    *,
    low_v: float = 0.22,
    mid_v: float = 0.55,
    high_v: float = 0.90,
    low_s: float = 0.25,
    mid_s: float = 0.60,
    high_s: float = 0.90,
) -> tuple[ColorRGB, ColorRGB, ColorRGB]:
    """
    Generate (low, mid, high) variants from a single anchor color.

    Uses anchor hue and maps saturation/value into provided bands.
    """
    h, s, v = rgb_to_hsv(anchor)

    low = hsv_to_rgb(h, clamp01(low_s * s), clamp01(low_v))
    mid = hsv_to_rgb(h, clamp01(mid_s * s), clamp01(mid_v))
    high = hsv_to_rgb(h, clamp01(high_s * s), clamp01(high_v))
    return low, mid, high


def fg_variants(bg: ColorRGB) -> tuple[ColorRGB, ColorRGB]:
    """
    Return (primary_fg, secondary_fg) for a background.

    Secondary foreground is a blended version used for quieter labels/metadata.
    """
    fg = auto_fg_color(bg)
    secondary = blend_rgb(fg, bg, 0.35)
    return fg, secondary


# ─────────────────────────────────────────────────────────────
# Parsing
# ─────────────────────────────────────────────────────────────


def parse_color_rgb(s: str) -> ColorRGB:
    """
    Parse a user-facing color string into ColorRGB.

    Supported formats:
      - "#RRGGBB"
      - "R,G,B" (0..255)
      - "rgb(R,G,B)" (0..255)
      - common names are intentionally not supported here (keep this helper lightweight)

    Raises:
      - ValueError on malformed strings
    """
    raw = s.strip()

    # "#RRGGBB"
    if raw.startswith("#") and len(raw) == 7:
        try:
            r = int(raw[1:3], 16)
            g = int(raw[3:5], 16)
            b = int(raw[5:7], 16)
            return ColorRGB(r, g, b)
        except Exception as e:
            raise ValueError(f"Invalid hex color: {s!r}") from e

    # "rgb(R,G,B)"
    if raw.lower().startswith("rgb(") and raw.endswith(")"):
        inner = raw[4:-1].strip()
        parts = [p.strip() for p in inner.split(",")]
        if len(parts) != 3:
            raise ValueError(f"Invalid rgb() color: {s!r}")
        r, g, b = (int(parts[0]), int(parts[1]), int(parts[2]))
        return normalize_rgb(ColorRGB(r, g, b))

    # "R,G,B"
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) == 3:
        r, g, b = (int(parts[0]), int(parts[1]), int(parts[2]))
        return normalize_rgb(ColorRGB(r, g, b))

    raise ValueError(f"Unrecognized color format: {s!r}")

@dataclass(frozen=True)
class ColorVariants:
    """
    A small container grouping commonly used color variants derived
    from a single anchor color.

    This is a convenience value object to avoid passing around
    loosely-structured tuples.

    Typical usage:
      variants = ColorVariants.from_anchor(base_color)
      bg = variants.mid
      fg = variants.fg_primary
    """

    anchor: ColorRGB

    # Background / surface variants
    low: ColorRGB
    mid: ColorRGB
    high: ColorRGB

    # Foreground variants (for text/icons on mid/high backgrounds)
    fg_primary: ColorRGB
    fg_secondary: ColorRGB

    # Accent colors
    accent_low: ColorRGB
    accent_strong: ColorRGB

    @classmethod
    def from_anchor(cls, anchor: ColorRGB) -> "ColorVariants":
        """
        Build a full ColorVariants set from an anchor color.

        Internally delegates to helpers in this module.
        """
        low, mid, high = variants_from_anchor(anchor)
        fg_primary, fg_secondary = fg_variants(mid)

        return cls(
            anchor=anchor,
            low=low,
            mid=mid,
            high=high,
            fg_primary=fg_primary,
            fg_secondary=fg_secondary,
            accent_low=accent_low(anchor),
            accent_strong=accent_strong(anchor),
        )