# tests/fs/test_atomic.py
# Tests for helpers.fs atomic write helpers (atomic_write_text / atomic_write_bytes / atomic_write_json).

from __future__ import annotations

from pathlib import Path

from helpers.fs import (
    atomic_write_bytes,
    atomic_write_json,
    atomic_write_text,
    read_bytes,
    read_json,
    read_text,
)


def test_atomic_write_text_creates_and_overwrites(tmp_path: Path) -> None:
    """atomic_write_text() should create and atomically overwrite files."""
    p = tmp_path / "a" / "file.txt"
    atomic_write_text(p, "one", encoding="utf-8")
    assert read_text(p, encoding="utf-8") == "one"

    atomic_write_text(p, "two", encoding="utf-8")
    assert read_text(p, encoding="utf-8") == "two"


def test_atomic_write_bytes_creates_and_overwrites(tmp_path: Path) -> None:
    """atomic_write_bytes() should create and atomically overwrite files."""
    p = tmp_path / "blob.bin"
    atomic_write_bytes(p, b"\x00\x01")
    assert read_bytes(p) == b"\x00\x01"

    atomic_write_bytes(p, b"\x02\x03\x04")
    assert read_bytes(p) == b"\x02\x03\x04"


def test_atomic_write_json_roundtrip(tmp_path: Path) -> None:
    """atomic_write_json() should write JSON that read_json() can load."""
    p = tmp_path / "state.json"
    atomic_write_json(p, {"b": 2, "a": 1}, indent=2, sort_keys=True)
    obj = read_json(p)
    assert obj == {"a": 1, "b": 2}

    # Overwrite
    atomic_write_json(p, {"x": {"y": [1, 2, 3]}}, indent=2, sort_keys=True)
    obj2 = read_json(p)
    assert obj2 == {"x": {"y": [1, 2, 3]}}
