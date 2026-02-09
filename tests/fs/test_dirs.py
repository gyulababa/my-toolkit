# tests/fs/test_dirs.py
# Tests for helpers.fs directory/path utilities (create, list, walk, safe-join, within-root guard, copy/move/delete).

from __future__ import annotations

from pathlib import Path

import pytest

from helpers.fs import (
    copy_file,
    ensure_dir,
    ensure_parent,
    find_upwards,
    ls,
    move,
    path_is_within,
    rm,
    rmdir,
    safe_join,
    walk_files,
)


def test_ensure_dir_creates(tmp_path: Path) -> None:
    """ensure_dir() should create nested directories and return the Path."""
    p = tmp_path / "a" / "b" / "c"
    assert not p.exists()
    out = ensure_dir(p)
    assert out.exists()
    assert out.is_dir()
    assert out == p


def test_ensure_parent_creates_parent(tmp_path: Path) -> None:
    """ensure_parent() should create the parent directory for a file path."""
    file_path = tmp_path / "x" / "y" / "file.txt"
    assert not file_path.parent.exists()
    out = ensure_parent(file_path)
    assert out.exists()
    assert out.is_dir()
    assert out == file_path.parent


def test_ls_nonexistent_returns_empty(tmp_path: Path) -> None:
    """ls() should return [] for missing directories."""
    missing = tmp_path / "missing"
    assert ls(missing) == []


def test_ls_pattern_and_recursive(tmp_path: Path) -> None:
    """ls() should support glob pattern and recursive traversal."""
    ensure_dir(tmp_path / "root" / "sub")
    (tmp_path / "root" / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "root" / "b.json").write_text("b", encoding="utf-8")
    (tmp_path / "root" / "sub" / "c.txt").write_text("c", encoding="utf-8")

    root = tmp_path / "root"
    nonrec = ls(root, pattern="*.txt", recursive=False)
    assert sorted([p.name for p in nonrec]) == ["a.txt"]

    rec = ls(root, pattern="*.txt", recursive=True)
    assert sorted([p.name for p in rec]) == ["a.txt", "c.txt"]


def test_walk_files_only_files(tmp_path: Path) -> None:
    """walk_files() should exclude directories and return only file Paths."""
    ensure_dir(tmp_path / "d1" / "d2")
    (tmp_path / "d1" / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "d1" / "d2" / "b.txt").write_text("b", encoding="utf-8")

    files = walk_files(tmp_path, pattern="*.txt", recursive=True)
    assert sorted([p.name for p in files]) == ["a.txt", "b.txt"]
    assert all(p.is_file() for p in files)


def test_find_upwards_marker(tmp_path: Path) -> None:
    """find_upwards() should locate the first parent containing any marker."""
    root = tmp_path / "project"
    sub = root / "a" / "b"
    ensure_dir(sub)
    (root / "pyproject.toml").write_text("[tool]\n", encoding="utf-8")

    found = find_upwards(sub, markers=["pyproject.toml", ".git"])
    assert found == root.resolve()

    not_found = find_upwards(sub, markers=["NOPE.marker"])
    assert not_found is None


def test_path_is_within(tmp_path: Path) -> None:
    """path_is_within() should detect whether a child resolves within parent."""
    parent = tmp_path / "parent"
    child = parent / "a" / "b"
    ensure_dir(child)

    assert path_is_within(child, parent) is True
    assert path_is_within(parent, parent) is True
    assert path_is_within(tmp_path, parent) is False


def test_safe_join_prevents_escape(tmp_path: Path) -> None:
    """safe_join() should raise if the join escapes the root."""
    root = tmp_path / "root"
    ensure_dir(root)

    ok = safe_join(root, "a", "b.txt")
    assert path_is_within(ok, root)

    # Attempt to escape via ..
    with pytest.raises(ValueError):
        safe_join(root, "..", "escape.txt")


def test_copy_move_rm_rmdir(tmp_path: Path) -> None:
    """Basic coverage for copy_file(), move(), rm(), and rmdir()."""
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    ensure_dir(src_dir)
    ensure_dir(dst_dir)

    src = src_dir / "file.txt"
    src.write_text("hello", encoding="utf-8")

    copied = copy_file(src, dst_dir / "file.txt")
    assert copied.exists()
    assert copied.read_text(encoding="utf-8") == "hello"

    moved = move(copied, dst_dir / "moved.txt")
    assert moved.exists()
    assert not (dst_dir / "file.txt").exists()

    rm(moved)
    assert not moved.exists()

    # rmdir non-recursive should fail on non-empty
    (dst_dir / "keep.txt").write_text("x", encoding="utf-8")
    with pytest.raises(OSError):
        rmdir(dst_dir, recursive=False, missing_ok=False)

    # recursive remove should succeed
    rmdir(dst_dir, recursive=True, missing_ok=False)
    assert not dst_dir.exists()
