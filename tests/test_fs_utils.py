# tests/test_fs_utils.py
from __future__ import annotations

import os
from pathlib import Path

import pytest

from helpers.fs import (
    ensure_dir,
    ls,
    find_upwards,
    path_is_within,
    read_text,
    write_text,
    atomic_write_text,
    read_bytes,
    write_bytes,
    read_json,
    write_json,
    atomic_write_json,
)


def test_ensure_dir(tmp_path: Path):
    p = tmp_path / "a" / "b" / "c"
    out = ensure_dir(p)
    assert out.exists()
    assert out.is_dir()


def test_ls(tmp_path: Path):
    (tmp_path / "a.txt").write_text("x", encoding="utf-8")
    (tmp_path / "b.log").write_text("y", encoding="utf-8")
    ensure_dir(tmp_path / "sub")
    (tmp_path / "sub" / "c.txt").write_text("z", encoding="utf-8")

    assert sorted([p.name for p in ls(tmp_path)]) == ["a.txt", "b.log", "sub"]
    assert sorted([p.name for p in ls(tmp_path, pattern="*.txt")]) == ["a.txt"]
    assert sorted([p.name for p in ls(tmp_path, pattern="*.txt", recursive=True)]) == ["a.txt", "c.txt"]


def test_find_upwards(tmp_path: Path):
    root = tmp_path / "root"
    ensure_dir(root)
    (root / "pyproject.toml").write_text("x", encoding="utf-8")

    nested = root / "a" / "b"
    ensure_dir(nested)
    found = find_upwards(nested, markers=["pyproject.toml"])
    assert found == root.resolve()


def test_path_is_within(tmp_path: Path):
    root = tmp_path / "root"
    ensure_dir(root)
    child = root / "a" / "b.txt"
    ensure_dir(child.parent)
    child.write_text("x", encoding="utf-8")
    assert path_is_within(child, root) is True

    other = tmp_path / "other" / "x.txt"
    ensure_dir(other.parent)
    other.write_text("y", encoding="utf-8")
    assert path_is_within(other, root) is False


def test_text_io(tmp_path: Path):
    p = tmp_path / "cfg" / "a.txt"
    write_text(p, "hello")
    assert read_text(p) == "hello"

    p2 = tmp_path / "cfg" / "atomic.txt"
    atomic_write_text(p2, "atomic")
    assert read_text(p2) == "atomic"


def test_bytes_io(tmp_path: Path):
    p = tmp_path / "bin" / "a.bin"
    write_bytes(p, b"\x01\x02\x03")
    assert read_bytes(p) == b"\x01\x02\x03"


def test_json_io(tmp_path: Path):
    p = tmp_path / "cfg" / "a.json"
    write_json(p, {"b": 2, "a": 1})
    doc = read_json(p)
    assert doc == {"a": 1, "b": 2}

    p2 = tmp_path / "cfg" / "atomic.json"
    atomic_write_json(p2, {"x": [1, 2, 3]})
    assert read_json(p2) == {"x": [1, 2, 3]}
