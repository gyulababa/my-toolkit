# helpers/toolkits/ui/spec/serde.py
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, cast

from .model import (
    CommandSpec,
    DockHint,
    MenuItem,
    MenuItemCommand,
    MenuItemSeparator,
    MenuItemSubmenu,
    MenuItemWindowToggle,
    MenuSpec,
    UiSpec,
    WindowSpec,
)
from .validate import validate_ui_spec


def _parse_menu_item(d: Dict[str, Any]) -> MenuItem:
    t = d.get("type")
    if t == "command":
        return MenuItemCommand(type="command", command_id=str(d["command_id"]))
    if t == "separator":
        return MenuItemSeparator(type="separator")
    if t == "window_toggle":
        return MenuItemWindowToggle(type="window_toggle", window_id=str(d["window_id"]))
    if t == "submenu":
        items_raw = d.get("items", [])
        items = [_parse_menu_item(cast(Dict[str, Any], x)) for x in items_raw]
        return MenuItemSubmenu(type="submenu", title=str(d["title"]), items=items)
    raise ValueError(f"Unknown menu item type: {t!r}")


def _parse_dock_hint(d: Any) -> DockHint | None:
    if d is None:
        return None
    if not isinstance(d, dict):
        raise ValueError("dock_hint must be an object or null")
    return DockHint(
        area=str(d.get("area", "center")),
        ratio=(float(d["ratio"]) if "ratio" in d and d["ratio"] is not None else None),
        target_window_id=(str(d["target_window_id"]) if d.get("target_window_id") else None),
    )


def load_ui_spec(path: str | Path) -> UiSpec:
    p = Path(path)
    raw = json.loads(p.read_text(encoding="utf-8"))

    commands = [
        CommandSpec(
            id=str(c["id"]),
            title=str(c["title"]),
            kind=str(c.get("kind", "app")),
            payload_schema=(str(c["payload_schema"]) if c.get("payload_schema") else None),
            enabled_when=(str(c["enabled_when"]) if c.get("enabled_when") else None),
        )
        for c in raw.get("commands", [])
    ]

    menus = []
    for m in raw.get("menus", []):
        items = [_parse_menu_item(x) for x in m.get("items", [])]
        menus.append(MenuSpec(id=str(m["id"]), title=str(m["title"]), items=items))

    windows = []
    for w in raw.get("windows", []):
        windows.append(
            WindowSpec(
                id=str(w["id"]),
                title=str(w["title"]),
                factory=str(w["factory"]),
                drawn_on_start=bool(w.get("drawn_on_start", True)),
                dock_hint=_parse_dock_hint(w.get("dock_hint")),
                menu_path=(list(w["menu_path"]) if w.get("menu_path") else None),
            )
        )

    spec = UiSpec(
        version=int(raw.get("version", 1)),
        commands=commands,
        menus=menus,
        windows=windows,
    )
    validate_ui_spec(spec)
    return spec


def dump_ui_spec(spec: UiSpec) -> Dict[str, Any]:
    # Dataclasses include nested unions; we prefer explicit emission for menu items.
    def dump_menu_item(item: MenuItem) -> Dict[str, Any]:
        if isinstance(item, MenuItemCommand):
            return {"type": "command", "command_id": item.command_id}
        if isinstance(item, MenuItemSeparator):
            return {"type": "separator"}
        if isinstance(item, MenuItemWindowToggle):
            return {"type": "window_toggle", "window_id": item.window_id}
        if isinstance(item, MenuItemSubmenu):
            return {"type": "submenu", "title": item.title, "items": [dump_menu_item(x) for x in item.items]}
        raise TypeError(f"Unsupported menu item: {type(item)}")

    out: Dict[str, Any] = {
        "version": spec.version,
        "commands": [asdict(c) for c in spec.commands],
        "menus": [
            {
                "id": m.id,
                "title": m.title,
                "items": [dump_menu_item(x) for x in m.items],
            }
            for m in spec.menus
        ],
        "windows": [
            {
                "id": w.id,
                "title": w.title,
                "factory": w.factory,
                "drawn_on_start": w.drawn_on_start,
                "dock_hint": (asdict(w.dock_hint) if w.dock_hint else None),
                "menu_path": w.menu_path,
            }
            for w in spec.windows
        ],
    }
    return out
