# helpers/toolkits/ui/state/migrate.py
from __future__ import annotations

from typing import Any, Dict


SUPPORTED_STATE_VERSIONS = {1}


def migrate_state_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Accept older UI state dicts and return latest dict structure.
    v1 is baseline.
    """
    v = int(d.get("version", 1))
    if v not in SUPPORTED_STATE_VERSIONS:
        raise ValueError(f"Unsupported UiState version: {v}")
    if v == 1:
        # Ensure keys exist with sane defaults.
        d.setdefault("active_layout_id", "default")
        d.setdefault("dock_layout_blob", None)
        d.setdefault("windows", {})
        d.setdefault("kv", {})
        d["version"] = 1
        return d
