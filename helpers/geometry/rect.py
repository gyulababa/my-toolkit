# helpers/geometry/rect.py
# Geometry primitives and rectangle/XYXY helpers (UI-agnostic; no rendering or widget logic).

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Tuple

from helpers.math.basic import clamp


@dataclass(frozen=True)
class RectF:
    """
    Immutable float rectangle, defined as (x, y, w, h).

    Conventions:
      - x/y are top-left in typical UI coordinate systems (but this is not enforced)
      - width/height may be 0; negative sizes are generally treated as invalid by helpers below
    """
    x: float
    y: float
    w: float
    h: float

    def right(self) -> float:
        """Return x + w."""
        return self.x + self.w

    def bottom(self) -> float:
        """Return y + h."""
        return self.y + self.h

    def contains(self, px: float, py: float) -> bool:
        """Return True if (px, py) lies inside this rectangle."""
        return (self.x <= px <= self.right()) and (self.y <= py <= self.bottom())

    def inset(self, dx: float, dy: float) -> "RectF":
        """Return a rectangle inset by (dx, dy) on all sides."""
        return RectF(self.x + dx, self.y + dy, self.w - 2 * dx, self.h - 2 * dy)

    def inflate(self, dx: float, dy: float) -> "RectF":
        """Return a rectangle expanded by (dx, dy) on all sides."""
        return RectF(self.x - dx, self.y - dy, self.w + 2 * dx, self.h + 2 * dy)


def clamp_rect_to_bounds(r: RectF, bounds: RectF) -> RectF:
    """
    Clamp a rectangle to stay within bounds, potentially shrinking it.

    This is useful for keeping viewports/ROIs within a known surface.
    """
    x0 = clamp(r.x, bounds.x, bounds.right())
    y0 = clamp(r.y, bounds.y, bounds.bottom())
    x1 = clamp(r.right(), bounds.x, bounds.right())
    y1 = clamp(r.bottom(), bounds.y, bounds.bottom())
    return RectF(x0, y0, max(0.0, x1 - x0), max(0.0, y1 - y0))


def fit_aspect(
    src_w: float,
    src_h: float,
    dst_w: float,
    dst_h: float,
    mode: Literal["contain", "cover"] = "contain",
) -> tuple[float, float]:
    """
    Compute a scaled size that preserves source aspect ratio within/outside a destination.

    mode:
      - "contain": letterbox (fits entirely inside)
      - "cover": crop (covers destination fully)
    """
    if src_w <= 0 or src_h <= 0 or dst_w <= 0 or dst_h <= 0:
        return 0.0, 0.0

    src_aspect = src_w / src_h
    dst_aspect = dst_w / dst_h

    if (mode == "contain" and src_aspect > dst_aspect) or (mode == "cover" and src_aspect < dst_aspect):
        # Fit width
        w = dst_w
        h = dst_w / src_aspect
    else:
        # Fit height
        h = dst_h
        w = dst_h * src_aspect

    return w, h


def fit_aspect_rect(
    src_w: float,
    src_h: float,
    dst: RectF,
    mode: Literal["contain", "cover"] = "contain",
    *,
    align_x: float = 0.5,
    align_y: float = 0.5,
) -> RectF:
    """
    Return a destination RectF that positions an aspect-preserving scaled source inside dst.

    align_x/align_y:
      - 0.0: left/top
      - 0.5: center
      - 1.0: right/bottom
    """
    w, h = fit_aspect(src_w, src_h, dst.w, dst.h, mode=mode)
    x = dst.x + (dst.w - w) * clamp(align_x, 0.0, 1.0)
    y = dst.y + (dst.h - h) * clamp(align_y, 0.0, 1.0)
    return RectF(x, y, w, h)


# ─────────────────────────────────────────────────────────────
# XYXY helpers
# XYXY means: (x0, y0, x1, y1) in the same coordinate space.
# These helpers are neutral about inclusive/exclusive edges; treat values as continuous.
# ─────────────────────────────────────────────────────────────


def normalize_xyxy(x0: float, y0: float, x1: float, y1: float) -> tuple[float, float, float, float]:
    """Return XYXY ordered so that x0<=x1 and y0<=y1."""
    return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def xyxy_is_valid(x0: float, y0: float, x1: float, y1: float) -> bool:
    """Return True if the rectangle defined by XYXY has positive area."""
    x0, y0, x1, y1 = normalize_xyxy(x0, y0, x1, y1)
    return (x1 - x0) > 0 and (y1 - y0) > 0


def clamp_xyxy_to_bounds(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    *,
    w: float,
    h: float,
) -> tuple[float, float, float, float]:
    """Clamp XYXY coordinates to stay within [0..w]x[0..h]."""
    x0, y0, x1, y1 = normalize_xyxy(x0, y0, x1, y1)
    x0 = clamp(x0, 0.0, w)
    y0 = clamp(y0, 0.0, h)
    x1 = clamp(x1, 0.0, w)
    y1 = clamp(y1, 0.0, h)
    return x0, y0, x1, y1


def clamp_xyxy_preserve_size(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    *,
    w: float,
    h: float,
) -> tuple[float, float, float, float]:
    """
    Clamp XYXY to bounds while preserving the rectangle size where possible.

    If the rectangle is larger than the bounds in either dimension, it will be clamped and shrink.
    """
    x0, y0, x1, y1 = normalize_xyxy(x0, y0, x1, y1)
    rw = max(0.0, x1 - x0)
    rh = max(0.0, y1 - y0)

    if rw > w:
        x0, x1 = 0.0, w
    else:
        x0 = clamp(x0, 0.0, w - rw)
        x1 = x0 + rw

    if rh > h:
        y0, y1 = 0.0, h
    else:
        y0 = clamp(y0, 0.0, h - rh)
        y1 = y0 + rh

    return x0, y0, x1, y1


def xyxy_px_to_norm(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    *,
    w: float,
    h: float,
) -> tuple[float, float, float, float]:
    """
    Convert XYXY from pixel coordinates to normalized [0..1] space.

    Assumes:
      - w/h are the full pixel bounds
      - caller handles w/h > 0
    """
    if w <= 0 or h <= 0:
        return 0.0, 0.0, 0.0, 0.0
    x0, y0, x1, y1 = normalize_xyxy(x0, y0, x1, y1)
    return (x0 / w, y0 / h, x1 / w, y1 / h)


def xyxy_norm_to_px(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    *,
    w: float,
    h: float,
    rounding: Literal["floor", "round", "ceil"] = "round",
) -> tuple[int, int, int, int]:
    """
    Convert normalized [0..1] XYXY into pixel coordinates.

    rounding controls how float coordinates are quantized.
    """
    import math

    x0, y0, x1, y1 = normalize_xyxy(x0, y0, x1, y1)
    fx0, fy0, fx1, fy1 = (x0 * w, y0 * h, x1 * w, y1 * h)

    if rounding == "floor":
        return (int(math.floor(fx0)), int(math.floor(fy0)), int(math.floor(fx1)), int(math.floor(fy1)))
    if rounding == "ceil":
        return (int(math.ceil(fx0)), int(math.ceil(fy0)), int(math.ceil(fx1)), int(math.ceil(fy1)))
    return (int(round(fx0)), int(round(fy0)), int(round(fx1)), int(round(fy1)))
