# helpers/toolkits/ui/runtime/menu_enrich.py
from __future__ import annotations

from typing import List, Set

from helpers.toolkits.ui.spec.models import (
    MenuItem,
    MenuItemCommand,
    MenuItemSeparator,
    MenuItemSubmenu,
    MenuItemWindowToggle,
    MenuSpec,
    UiSpec,
)


def enrich_menus(spec: UiSpec) -> List[MenuSpec]:
    menus = list(spec.menus)
    menus = _ensure_default_file_help(spec, menus)
    menus = _ensure_view_toggles(spec, menus)
    return menus


def _ensure_default_file_help(spec: UiSpec, menus: List[MenuSpec]) -> List[MenuSpec]:
    titles = [m.title for m in menus]
    cmd_ids = spec.command_ids()
    out = list(menus)

    if "File" not in titles:
        file_items: List[MenuItem] = []
        if "app.quit" in cmd_ids:
            file_items.append(MenuItemCommand(type="command", command_id="app.quit"))
        out.append(MenuSpec(id="file", title="File", items=file_items))

    if "Help" not in titles:
        help_items: List[MenuItem] = []
        # If there is an about window, add it as a toggle
        about_candidates = [
            w.id
            for w in spec.windows
            if w.id.endswith("about") or w.id.endswith(".about") or w.id == "win.about"
        ]
        if about_candidates:
            help_items.append(MenuItemWindowToggle(type="window_toggle", window_id=about_candidates[0]))
        out.append(MenuSpec(id="help", title="Help", items=help_items))

    return out


def _ensure_view_toggles(spec: UiSpec, menus: List[MenuSpec]) -> List[MenuSpec]:
    view_idx = None
    for i, m in enumerate(menus):
        if m.title == "View":
            view_idx = i
            break

    out = list(menus)
    if view_idx is None:
        out.append(MenuSpec(id="view", title="View", items=[]))
        view_idx = len(out) - 1

    view_menu = out[view_idx]

    existing: Set[str] = set()

    def walk(items: List[MenuItem]) -> None:
        for it in items:
            if isinstance(it, MenuItemWindowToggle):
                existing.add(it.window_id)
            elif isinstance(it, MenuItemSubmenu):
                walk(it.items)

    walk(view_menu.items)

    new_items = list(view_menu.items)
    for w in spec.windows:
        if w.id not in existing:
            new_items.append(MenuItemWindowToggle(type="window_toggle", window_id=w.id))

    out[view_idx] = MenuSpec(id=view_menu.id, title=view_menu.title, items=new_items)
    return out
