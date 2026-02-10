# app/adapters/dearpygui/ui/dpg_menu_builder.py
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from helpers.toolkits.ui.spec import (
    MenuItem,
    MenuItemCommand,
    MenuItemSeparator,
    MenuItemSubmenu,
    MenuItemWindowToggle,
    MenuSpec,
)

def build_menu_bar(
    dpg: Any,
    menus: list[MenuSpec],
    *,
    command_title_by_id: Optional[Dict[str, str]] = None,
    window_title_by_id: Optional[Dict[str, str]] = None,
    on_command: Callable[[str, Optional[dict]], None],
    on_window_toggle: Callable[[str], None],
) -> None:
    command_titles = command_title_by_id or {}
    window_titles = window_title_by_id or {}
    with dpg.viewport_menu_bar():
        for m in menus:
            with dpg.menu(label=m.title):
                _build_menu_items(
                    dpg,
                    m.items,
                    command_titles,
                    window_titles,
                    on_command,
                    on_window_toggle,
                )

def _build_menu_items(
    dpg: Any,
    items: list[MenuItem],
    command_title_by_id: Dict[str, str],
    window_title_by_id: Dict[str, str],
    on_command: Callable[[str, Optional[dict]], None],
    on_window_toggle: Callable[[str], None],
) -> None:
    for it in items:
        if isinstance(it, MenuItemCommand):
            label = command_title_by_id.get(it.command_id, it.command_id)
            dpg.add_menu_item(
                label=label,
                callback=lambda s, a, u, cid=it.command_id: on_command(cid, None),
            )
        elif isinstance(it, MenuItemWindowToggle):
            label = window_title_by_id.get(it.window_id, it.window_id)
            dpg.add_menu_item(
                label=label,
                callback=lambda s, a, u, wid=it.window_id: on_window_toggle(wid),
            )
        elif isinstance(it, MenuItemSeparator):
            dpg.add_separator()
        elif isinstance(it, MenuItemSubmenu):
            with dpg.menu(label=it.title):
                _build_menu_items(
                    dpg,
                    it.items,
                    command_title_by_id,
                    window_title_by_id,
                    on_command,
                    on_window_toggle,
                )
        else:
            raise TypeError(f"Unsupported menu item: {type(it)}")
