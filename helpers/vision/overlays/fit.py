# helpers/vision/overlays/fit.py
# Fit transform between source frame space and surface (stage) space.

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Tuple

from helpers.geometry.rect import RectF, fit_aspect_rect


FitMode = Literal["contain", "cover", "stretch"]


@dataclass(frozen=True)
class FitTransform:
    src_w: int
    src_h: int
    surface_w: int
    surface_h: int
    mode: FitMode = "contain"
    draw_rect: RectF = RectF(0, 0, 0, 0)

    @staticmethod
    def compute(*, src_w: int, src_h: int, surface_w: int, surface_h: int, mode: FitMode) -> "FitTransform":
        surface_rect = RectF(0.0, 0.0, float(surface_w), float(surface_h))
        if mode == "stretch":
            draw_rect = surface_rect
        else:
            draw_rect = fit_aspect_rect(src_w, src_h, surface_rect, mode=mode)
        return FitTransform(src_w=src_w, src_h=src_h, surface_w=surface_w, surface_h=surface_h, mode=mode, draw_rect=draw_rect)

    def src_to_surface(self, x: float, y: float) -> Tuple[float, float]:
        # Uniform scale in contain/cover, non-uniform in stretch.
        if self.src_w <= 0 or self.src_h <= 0:
            return (self.draw_rect.x, self.draw_rect.y)

        sx = self.draw_rect.w / float(self.src_w)
        sy = self.draw_rect.h / float(self.src_h)
        return (self.draw_rect.x + x * sx, self.draw_rect.y + y * sy)

    def surface_to_src(self, x: float, y: float) -> Tuple[float, float]:
        if self.src_w <= 0 or self.src_h <= 0:
            return (0.0, 0.0)
        sx = self.draw_rect.w / float(self.src_w) if self.src_w else 1.0
        sy = self.draw_rect.h / float(self.src_h) if self.src_h else 1.0
        return ((x - self.draw_rect.x) / sx, (y - self.draw_rect.y) / sy)

    def norm_to_surface(self, nx: float, ny: float) -> Tuple[float, float]:
        # normalized relative to draw rect
        return (self.draw_rect.x + nx * self.draw_rect.w, self.draw_rect.y + ny * self.draw_rect.h)
