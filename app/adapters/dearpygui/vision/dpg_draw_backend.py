# app/adapters/dearpygui/vision/dpg_draw_backend.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

from app.adapters.dearpygui.vision.dpg_texture_pool import TextureRef

Point = Tuple[float, float]
RGBA = Tuple[int, int, int, int]


@dataclass(frozen=True)
class StrokeStyle:
    color: RGBA = (255, 255, 255, 255)
    thickness: float = 1.0


@dataclass(frozen=True)
class FillStyle:
    color: RGBA = (0, 0, 0, 0)


@dataclass(frozen=True)
class TextStyle:
    color: RGBA = (255, 255, 255, 255)
    size: int = 16


class DpgDrawBackend:
    """
    Draw primitives on a drawlist. Clear-per-frame strategy.
    """

    def __init__(self, *, dpg, drawlist_tag: str):
        self._dpg = dpg
        self._drawlist_tag = drawlist_tag

    def clear(self) -> None:
        self._dpg.delete_item(self._drawlist_tag, children_only=True)

    def image(self, tex: TextureRef, *, pmin: Point, pmax: Point, tint: Optional[RGBA] = None) -> None:
        kwargs = {}
        if tint is not None:
            kwargs["tint_color"] = tint
        self._dpg.draw_image(tex.texture_tag, pmin, pmax, parent=self._drawlist_tag, **kwargs)

    def rect(self, *, pmin: Point, pmax: Point, stroke=None, fill=None) -> None:
        # allow dict-style input from render.py (keeps that module toolkit-agnostic)
        if isinstance(stroke, dict):
            stroke = StrokeStyle(color=stroke.get("color", (255, 255, 255, 255)), thickness=float(stroke.get("thickness", 1.0)))
        if isinstance(fill, dict):
            fill = FillStyle(color=fill.get("color", (0, 0, 0, 0)))

        stroke = stroke or StrokeStyle()
        fill = fill or FillStyle()

        self._dpg.draw_rectangle(
            pmin,
            pmax,
            color=stroke.color,
            fill=fill.color,
            thickness=stroke.thickness,
            parent=self._drawlist_tag,
        )

    def line(self, p1: Point, p2: Point, *, stroke=None) -> None:
        if isinstance(stroke, dict):
            stroke = StrokeStyle(color=stroke.get("color", (255, 255, 255, 255)), thickness=float(stroke.get("thickness", 1.0)))
        stroke = stroke or StrokeStyle()

        self._dpg.draw_line(p1, p2, color=stroke.color, thickness=stroke.thickness, parent=self._drawlist_tag)

    def polyline(self, points: Sequence[Point], *, closed: bool = False, stroke=None) -> None:
        if isinstance(stroke, dict):
            stroke = StrokeStyle(color=stroke.get("color", (255, 255, 255, 255)), thickness=float(stroke.get("thickness", 1.0)))
        stroke = stroke or StrokeStyle()

        pts = list(points)
        if closed and len(pts) >= 2:
            pts.append(pts[0])

        self._dpg.draw_polyline(pts, color=stroke.color, thickness=stroke.thickness, parent=self._drawlist_tag)

    def text(self, pos: Point, text: str, *, style=None) -> None:
        if isinstance(style, dict):
            style = TextStyle(color=style.get("color", (255, 255, 255, 255)), size=int(style.get("size", 16)))
        style = style or TextStyle()

        self._dpg.draw_text(pos, text, color=style.color, size=style.size, parent=self._drawlist_tag)
