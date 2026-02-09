# helpers/color/__init__.py
# helpers/color/__init__.py
"""helpers.color

Small, UI-agnostic color helpers.

Public API is centered around:
- ColorRGB: simple (r,g,b) container
- parsing and basic transforms (HSV conversion, blending, luminance)
- generating accent/variant palettes
"""

from .color_types import ColorRGB
from .color_utils import (
    ColorVariants,
    normalize_rgb,
    rgb_to_hsv,
    hsv_to_rgb,
    blend_rgb,
    relative_luminance,
    auto_fg_color,
    opposite_hue_color,
    opposite_contrast_color,
    inverted_rgb,
    accent_low,
    accent_strong,
    variants_from_anchor,
    fg_variants,
    parse_color_rgb,
)

__all__ = [
    "ColorRGB",
    "ColorVariants",
    "normalize_rgb",
    "rgb_to_hsv",
    "hsv_to_rgb",
    "blend_rgb",
    "relative_luminance",
    "auto_fg_color",
    "opposite_hue_color",
    "opposite_contrast_color",
    "inverted_rgb",
    "accent_low",
    "accent_strong",
    "variants_from_anchor",
    "fg_variants",
    "parse_color_rgb",
]
