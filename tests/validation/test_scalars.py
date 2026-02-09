# tests/validation/test_scalars.py
# Tests for helpers.validation scalar validators (ensure_*).

from __future__ import annotations

from pathlib import Path

import pytest

from helpers.validation import (
    ValidationError,
    ensure_dict_of_str,
    ensure_enum_name,
    ensure_float,
    ensure_int,
    ensure_ip,
    ensure_list_of_str,
    ensure_pathlike,
    ensure_regex,
    ensure_str,
)


def test_ensure_str_strips_and_rejects_empty() -> None:
    """ensure_str should strip whitespace and reject empty strings by default."""
    assert ensure_str("  a  ", path="p") == "a"
    with pytest.raises(ValidationError):
        ensure_str("   ", path="p")


def test_ensure_int_rejects_bool_and_bounds() -> None:
    """ensure_int should reject bool and enforce min/max when provided."""
    with pytest.raises(ValidationError):
        ensure_int(True, path="x")  # type: ignore[arg-type]

    assert ensure_int(5, path="x", min_v=1, max_v=10) == 5

    with pytest.raises(ValidationError):
        ensure_int(0, path="x", min_v=1)

    with pytest.raises(ValidationError):
        ensure_int(11, path="x", max_v=10)


def test_ensure_float_accepts_int_rejects_bool() -> None:
    """ensure_float should accept ints and floats, reject bool."""
    assert ensure_float(5, path="x") == 5.0
    assert ensure_float(5.5, path="x") == 5.5
    with pytest.raises(ValidationError):
        ensure_float(False, path="x")  # type: ignore[arg-type]


def test_ensure_list_of_str_and_dict_of_str() -> None:
    """List/dict string validators should strip values."""
    assert ensure_list_of_str([" a ", "b"], path="v") == ["a", "b"]
    assert ensure_dict_of_str({"k": " v "}, path="v") == {"k": "v"}

    with pytest.raises(ValidationError):
        ensure_list_of_str([1], path="v")  # type: ignore[list-item]


def test_ensure_ip_versions() -> None:
    """ensure_ip should validate and optionally enforce IP version."""
    assert ensure_ip("192.168.0.1", path="ip") == "192.168.0.1"
    with pytest.raises(ValidationError):
        ensure_ip("192.168.0.1", path="ip", version=6)


def test_ensure_pathlike_accepts_str_and_path(tmp_path: Path) -> None:
    """ensure_pathlike should accept both str and Path."""
    p1 = ensure_pathlike(str(tmp_path / "a.txt"), path="p")
    assert isinstance(p1, Path)
    p2 = ensure_pathlike(tmp_path / "b.txt", path="p")
    assert isinstance(p2, Path)


def test_ensure_enum_name_and_regex() -> None:
    """ensure_enum_name and ensure_regex should validate patterns."""
    assert ensure_enum_name("A_B-1.ok", path="n") == "A_B-1.ok"
    with pytest.raises(ValidationError):
        ensure_enum_name("bad name!", path="n")

    rx = ensure_regex(r"^a+$", path="r")
    assert rx.match("aaa")

    with pytest.raises(ValidationError):
        ensure_regex(r"(", path="r")
