# helpers/geometry/__init__.py
"""helpers.geometry

Canonical geometry utilities.

Public surface is re-exported from helpers.geometry.rect.
"""

from .rect import (
    RectF,
    clamp_rect_to_bounds,
    fit_aspect,
    fit_aspect_rect,
    normalize_xyxy,
    xyxy_is_valid,
    clamp_xyxy_to_bounds,
    clamp_xyxy_preserve_size,
    xyxy_px_to_norm,
    xyxy_norm_to_px,
)

__all__ = [
    "RectF",
    "clamp_rect_to_bounds",
    "fit_aspect",
    "fit_aspect_rect",
    "normalize_xyxy",
    "xyxy_is_valid",
    "clamp_xyxy_to_bounds",
    "clamp_xyxy_preserve_size",
    "xyxy_px_to_norm",
    "xyxy_norm_to_px",
]
