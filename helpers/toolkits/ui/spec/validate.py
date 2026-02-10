# helpers/toolkits/ui/spec/validate.py
from __future__ import annotations

from .models import MenuItemCommand, MenuItemSubmenu, MenuItemWindowToggle, UiSpec


SUPPORTED_SPEC_VERSIONS = {1}


def validate_ui_spec(spec: UiSpec) -> None:
    if spec.version not in SUPPORTED_SPEC_VERSIONS:
        raise ValueError(f"Unsupported UiSpec version: {spec.version}")

    cmd_ids = [c.id for c in spec.commands]
    win_ids = [w.id for w in spec.windows]
    if len(set(cmd_ids)) != len(cmd_ids):
        raise ValueError("Duplicate command IDs in UiSpec")
    if len(set(win_ids)) != len(win_ids):
        raise ValueError("Duplicate window IDs in UiSpec")

    cmd_id_set = set(cmd_ids)
    win_id_set = set(win_ids)

    def walk_items(items):
        for it in items:
            if isinstance(it, MenuItemCommand):
                if it.command_id not in cmd_id_set:
                    raise ValueError(f"Menu references unknown command_id: {it.command_id}")
            elif isinstance(it, MenuItemWindowToggle):
                if it.window_id not in win_id_set:
                    raise ValueError(f"Menu references unknown window_id: {it.window_id}")
            elif isinstance(it, MenuItemSubmenu):
                walk_items(it.items)

    for m in spec.menus:
        walk_items(m.items)

    for w in spec.windows:
        if not w.factory.strip():
            raise ValueError(f"Window {w.id} has empty factory key")
        if w.factory_args is not None and not isinstance(w.factory_args, dict):
            raise ValueError(f"Window {w.id} factory_args must be an object")
        if w.factory_args_ref is not None and not str(w.factory_args_ref).strip():
            raise ValueError(f"Window {w.id} factory_args_ref must be a non-empty string when set")
        if w.menu_path is not None and any(not str(seg).strip() for seg in w.menu_path):
            raise ValueError(f"Window {w.id} menu_path entries must be non-empty strings")
