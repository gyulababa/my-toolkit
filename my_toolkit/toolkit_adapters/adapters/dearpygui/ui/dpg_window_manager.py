# app/adapters/dearpygui/ui/dpg_window_manager.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from helpers.toolkits.ui.spec import WindowSpec
from helpers.toolkits.ui.state import WindowState
from helpers.toolkits.ui.runtime import ExtraStateHooks


@dataclass
class DpgWindowHandle:
    dpg: Any
    window_id: str
    window_tag: str
    hooks: Optional[ExtraStateHooks] = None

    def set_open(self, is_open: bool) -> None:
        self.dpg.configure_item(self.window_tag, show=is_open)

    def is_open(self) -> bool:
        cfg = self.dpg.get_item_configuration(self.window_tag)
        return bool(cfg.get("show", True))

    def apply_state(self, state: WindowState) -> None:
        self.set_open(state.is_open)
        if state.pos_xy is not None:
            self.dpg.set_item_pos(self.window_tag, state.pos_xy)
        if state.size_wh is not None:
            self.dpg.set_item_width(self.window_tag, state.size_wh[0])
            self.dpg.set_item_height(self.window_tag, state.size_wh[1])

        if self.hooks is not None:
            self.hooks.load_extra(dict(state.extra or {}))

    def capture_state(self) -> WindowState:
        is_open = self.is_open()
        pos = tuple(self.dpg.get_item_pos(self.window_tag))
        size = (int(self.dpg.get_item_width(self.window_tag)), int(self.dpg.get_item_height(self.window_tag)))
        extra: dict = {}
        if self.hooks is not None:
            extra = dict(self.hooks.save_extra() or {})

        return WindowState(
            id=self.window_id,
            is_open=is_open,
            pos_xy=(int(pos[0]), int(pos[1])),
            size_wh=size,
            extra=extra,
        )


class DpgWindowManager:
    def __init__(self, dpg: Any) -> None:
        self.dpg = dpg
        self.handles: Dict[str, DpgWindowHandle] = {}

    def create_window_container(self, spec: WindowSpec) -> str:
        tag = f"win::{spec.id}"
        with self.dpg.window(label=spec.title, tag=tag, show=True):
            pass
        return tag

    def bind_handle(self, spec: WindowSpec, window_tag: str, hooks: Optional[ExtraStateHooks]) -> DpgWindowHandle:
        h = DpgWindowHandle(dpg=self.dpg, window_id=spec.id, window_tag=window_tag, hooks=hooks)
        self.handles[spec.id] = h
        return h
