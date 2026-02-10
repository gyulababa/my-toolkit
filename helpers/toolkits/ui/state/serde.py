# helpers/toolkits/ui/state/serde.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .migrate import migrate_state_dict
from .model import UiState, WindowState


def ensure_ui_state(raw: Dict[str, Any]) -> UiState:
    """
    Validate/normalize raw dict -> UiState (in-memory).
    Uses migrate_state_dict for versioning and fills defaults.
    """
    d = migrate_state_dict(dict(raw))

    windows: Dict[str, WindowState] = {}
    for win_id, ws in (d.get("windows", {}) or {}).items():
        pos = ws.get("pos_xy")
        size = ws.get("size_wh")
        windows[str(win_id)] = WindowState(
            id=str(win_id),
            is_open=bool(ws.get("is_open", True)),
            pos_xy=(tuple(pos) if pos is not None else None),    # type: ignore[arg-type]
            size_wh=(tuple(size) if size is not None else None),  # type: ignore[arg-type]
            docked_to=(str(ws["docked_to"]) if ws.get("docked_to") else None),
            extra=dict(ws.get("extra", {}) or {}),
        )

    return UiState(
        version=int(d.get("version", 1)),
        active_layout_id=str(d.get("active_layout_id", "default")),
        dock_layout_blob=(str(d["dock_layout_blob"]) if d.get("dock_layout_blob") else None),
        windows=windows,
        kv=dict(d.get("kv", {}) or {}),
    )


def load_ui_state(path: str | Path) -> UiState:
    p = Path(path)
    if not p.exists():
        return UiState()
    d = json.loads(p.read_text(encoding="utf-8"))
    return ensure_ui_state(d)


def dump_ui_state(state: UiState) -> Dict[str, Any]:
    return {
        "version": state.version,
        "active_layout_id": state.active_layout_id,
        "dock_layout_blob": state.dock_layout_blob,
        "windows": {
            win_id: {
                "is_open": ws.is_open,
                "pos_xy": list(ws.pos_xy) if ws.pos_xy is not None else None,
                "size_wh": list(ws.size_wh) if ws.size_wh is not None else None,
                "docked_to": ws.docked_to,
                "extra": ws.extra,
            }
            for win_id, ws in state.windows.items()
        },
        "kv": state.kv,
    }


def save_ui_state(path: str | Path, state: UiState) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dump_ui_state(state), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
