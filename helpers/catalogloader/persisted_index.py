# helpers/catalogloader/persisted_index.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from helpers.fs.json import read_json, atomic_write_json

from .persisted_paths import index_path

SCHEMA_NAME = "persist_index"
SCHEMA_VERSION = 1


@dataclass(frozen=True)
class PersistIndex:
    """
    Domain index stored at:
      <persist_root>/<domain>/index.json

    Minimal schema (v1):
      {
        "schema_name": "persist_index",
        "schema_version": 1,
        "active_id": "0001",
        "next_int": 2,
        "history": [{"op":"seed","doc_id":"0001","note": "...", "ts": "..."}] (optional)
      }
    """

    active_id: str
    next_int: int
    schema_name: str = SCHEMA_NAME
    schema_version: int = SCHEMA_VERSION
    history: Optional[list[dict]] = None


def _validate_raw(raw: Any, p: Path) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError(f"Persist index must be an object: {p}")

    schema_name = raw.get("schema_name")
    schema_version = raw.get("schema_version")
    active_id = raw.get("active_id")
    next_int = raw.get("next_int")

    if schema_name != SCHEMA_NAME:
        raise ValueError(f"Persist index missing/invalid 'schema_name': {p}")
    if schema_version != SCHEMA_VERSION:
        raise ValueError(f"Persist index missing/invalid 'schema_version': {p}")
    if not isinstance(active_id, str) or not active_id:
        raise ValueError(f"Persist index missing/invalid 'active_id': {p}")
    if not isinstance(next_int, int) or next_int < 1:
        raise ValueError(f"Persist index missing/invalid 'next_int': {p}")

    hist = raw.get("history")
    if hist is not None and not isinstance(hist, list):
        raise ValueError(f"Persist index 'history' must be a list: {p}")

    return raw


def load_index(persist_root: Path, domain: str) -> Optional[PersistIndex]:
    p = index_path(persist_root, domain)
    if not p.exists():
        return None
    try:
        raw = read_json(p, encoding="utf-8")
    except Exception as e:
        raise ValueError(f"Failed to read persist index: {p}") from e

    raw = _validate_raw(raw, p)
    hist = raw.get("history")
    return PersistIndex(active_id=raw["active_id"], next_int=raw["next_int"], history=hist)


def save_index(persist_root: Path, domain: str, idx: PersistIndex) -> None:
    p = index_path(persist_root, domain)

    if idx.schema_name != SCHEMA_NAME:
        raise ValueError(f"Persist index missing/invalid 'schema_name': {p}")
    if idx.schema_version != SCHEMA_VERSION:
        raise ValueError(f"Persist index missing/invalid 'schema_version': {p}")

    raw: Dict[str, Any] = {
        "schema_name": idx.schema_name,
        "schema_version": idx.schema_version,
        "active_id": idx.active_id,
        "next_int": idx.next_int,
    }
    if idx.history is not None:
        raw["history"] = idx.history

    atomic_write_json(p, raw, encoding="utf-8", indent=2, sort_keys=True)
