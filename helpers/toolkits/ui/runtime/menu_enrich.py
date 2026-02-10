# helpers/toolkits/ui/runtime/menu_enrich.py
from __future__ import annotations

from dataclasses import replace
from typing import List, Set

from helpers.toolkits.ui.spec import (
    MenuItem,
    MenuItemSubmenu,
    MenuItemWindowToggle,
    MenuSpec,
    UiSpec,
)


def enrich_menus_with_view_toggles(spec: UiSpec) -> List[MenuSpec]:
    """
    Ensure a top-level 'View' menu exists and contains window toggles for all windows in spec.
    - Does not remove or reorder existing items.
    - Avoids duplicates.
    """
    menus = list(spec.menus)

    view_idx = None
    for i, m in enumerate(menus):
        if m.title == "View":
            view_idx = i
            break

    if view_idx is None:
        # Create empty View menu at the end (predictable).
        menus.append(MenuSpec(id="view", title="View", items=[]))
        view_idx = len(menus) - 1

    view_menu = menus[view_idx]

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

    menus[view_idx] = MenuSpec(id=view_menu.id, title=view_menu.title, items=new_items)
    return menus
