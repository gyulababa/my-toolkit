# services/vision/stage_surface.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class StageSurfaceSpec:
    stage_tag: str = "stage"
    child_tag: str = "stage.child"
    drawlist_tag: str = "stage.drawlist"

    fill_parent: bool = True
    no_scrollbar: bool = True


class StageSurface:
    """
    DPG Stage container + sizing.

    Layout:
      stage(group)
        child_window (fill)
          drawlist (fill)

    The drawlist is the rendering target for video + overlays (via DpgDrawBackend).
    """

    def __init__(self, *, dpg, spec: StageSurfaceSpec):
        self._dpg = dpg
        self.spec = spec
        self._built = False
        self._last_size: Tuple[int, int] = (0, 0)

    def build(self, *, parent_tag: Optional[str] = None) -> None:
        dpg = self._dpg
        if self._built:
            return

        if parent_tag is not None:
            dpg.push_container_stack(parent_tag)
        try:
            with dpg.group(tag=self.spec.stage_tag):
                w = -1 if self.spec.fill_parent else 0
                h = -1 if self.spec.fill_parent else 0
                with dpg.child_window(
                    tag=self.spec.child_tag,
                    width=w,
                    height=h,
                    no_scrollbar=self.spec.no_scrollbar,
                ):
                    dpg.add_drawlist(tag=self.spec.drawlist_tag, width=-1, height=-1)
        finally:
            if parent_tag is not None:
                dpg.pop_container_stack()

        self._built = True

    def surface_size(self) -> Tuple[int, int]:
        dpg = self._dpg
        if not self._built:
            return (0, 0)
        try:
            w, h = dpg.get_item_rect_size(self.spec.child_tag)
        except Exception:
            w, h = self._last_size
        w = int(w) if w else 0
        h = int(h) if h else 0
        self._last_size = (w, h)
        return self._last_size

    @property
    def drawlist_tag(self) -> str:
        return self.spec.drawlist_tag
