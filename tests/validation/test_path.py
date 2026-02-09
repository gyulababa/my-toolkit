# tests/validation/test_path.py
# Focused tests for path validation helpers (ensure_pathlike / require_path / optional_path).

from __future__ import annotations

from pathlib import Path

import pytest

from helpers.validation import ValidationError, ensure_pathlike, optional_path, require_path


def test_ensure_pathlike_rejects_non_pathlike() -> None:
    """ensure_pathlike should reject unsupported types."""
    with pytest.raises(ValidationError):
        ensure_pathlike(123, path="p")  # type: ignore[arg-type]


def test_require_path_from_mapping(tmp_path: Path) -> None:
    """require_path should accept str and return Path."""
    d = {"file": str(tmp_path / "a.txt")}
    p = require_path(d, "file", path="cfg")
    assert isinstance(p, Path)
    assert str(p).endswith("a.txt")


def test_optional_path_returns_default() -> None:
    """optional_path should return default on missing or None."""
    assert optional_path({}, "x", default=None) is None
    assert optional_path({"x": None}, "x", default=Path("fallback")) == Path("fallback")
