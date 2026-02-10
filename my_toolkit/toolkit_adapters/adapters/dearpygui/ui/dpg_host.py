# app/adapters/dearpygui/ui/dpg_host.py
from __future__ import annotations

from typing import Any

from helpers.toolkits.ui.spec import WindowSpec
from helpers.toolkits.ui.runtime import UiHost, WindowFactoryRegistry, WindowHandle

from .dpg_menu_builder import build_menu_bar
from .dpg_window_manager import DpgWindowManager


class DpgHost(UiHost):
    def __init__(self, dpg: Any, factories: WindowFactoryRegistry) -> None:
        self.dpg = dpg
        self.factories = factories
        self.win_mgr = DpgWindowManager(dpg)
        self._quit = False

    def build_menus(self, spec_menus, on_command, on_window_toggle) -> None:
        build_menu_bar(self.dpg, spec_menus, on_command=on_command, on_window_toggle=on_window_toggle)

    def create_window(self, spec: WindowSpec, factory_key: str, ctx: Any) -> WindowHandle:
        window_tag = self.win_mgr.create_window_container(spec)

        # Build content *inside* the window
        with self.dpg.group(parent=window_tag):
            hooks = self.factories.build(factory_key, self, ctx, spec.id, window_tag)

        return self.win_mgr.bind_handle(spec, window_tag, hooks)

    def request_quit(self) -> None:
        self._quit = True

    @property
    def should_quit(self) -> bool:
        return self._quit
