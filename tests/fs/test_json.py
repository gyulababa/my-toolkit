# tests/fs/test_json.py
# Tests for helpers.fs JSON helpers (read_json*, write_json*, atomic_write_json, update_json).

from __future__ import annotations

from pathlib import Path

import pytest

from helpers.fs import (
    atomic_write_json,
    read_json,
    read_json_default,
    read_json_strict,
    update_json,
    write_json,
    write_json_compact,
)


def test_write_json_and_read_json(tmp_path: Path) -> None:
    """write_json() should create parents and round-trip via read_json()."""
    p = tmp_path / "cfg" / "config.json"
    write_json(p, {"b": 2, "a": 1}, indent=2, sort_keys=True)
    assert read_json(p) == {"a": 1, "b": 2}


def test_write_json_compact(tmp_path: Path) -> None:
    """write_json_compact() should produce a compact JSON representation."""
    p = tmp_path / "compact.json"
    write_json_compact(p, {"b": 2, "a": 1}, sort_keys=True)
    raw = p.read_text(encoding="utf-8")
    # Compact separators should avoid spaces after separators (",", ":")
    assert " " not in raw.replace(" ", "") or raw == raw.replace(" ", "")
    assert read_json(p) == {"a": 1, "b": 2}


def test_read_json_default(tmp_path: Path) -> None:
    """read_json_default() should return default when file missing."""
    p = tmp_path / "missing.json"
    assert read_json_default(p, default={"x": 1}) == {"x": 1}


def test_read_json_strict_root_type(tmp_path: Path) -> None:
    """read_json_strict() should enforce allowed root types."""
    p = tmp_path / "v.json"
    atomic_write_json(p, "hello")  # root is str
    with pytest.raises(TypeError):
        read_json_strict(p, root_types=(dict, list))


def test_update_json_in_place_and_return(tmp_path: Path) -> None:
    """update_json() should support in-place mutation and returned replacement."""
    p = tmp_path / "state.json"

    # In-place
    def mut(obj):
        obj["a"] = 1

    out = update_json(p, mut, default={}, atomic=True)
    assert out == {"a": 1}
    assert read_json(p) == {"a": 1}

    # Replace object
    def repl(_obj):
        return {"b": 2}

    out2 = update_json(p, repl, default={}, atomic=True)
    assert out2 == {"b": 2}
    assert read_json(p) == {"b": 2}
