# tests/validation/test_mapping.py
# Tests for helpers.validation mapping readers (require_* / optional_*), including net/path readers.

from __future__ import annotations

from pathlib import Path

import pytest

from helpers.validation import (
    ValidationError,
    optional_bool,
    optional_int,
    optional_path,
    optional_str,
    require_bool,
    require_endpoint,
    require_host,
    require_http_url,
    require_int,
    require_ip,
    require_list_of_str,
    require_path,
    require_port,
    require_str,
)


def test_require_str_missing_raises() -> None:
    """Missing required keys should raise ValidationError with a stable message."""
    d = {}
    with pytest.raises(ValidationError):
        require_str(d, "name", path="root")


def test_require_and_optional_readers_basic() -> None:
    """require_* should validate types; optional_* returns defaults on missing/None."""
    d = {"a": " hi ", "b": 3, "c": True, "n": None}

    assert require_str(d, "a") == "hi"
    assert require_int(d, "b", min_v=1) == 3
    assert require_bool(d, "c") is True

    assert optional_str(d, "missing", default="x") == "x"
    assert optional_int(d, "missing", default=7) == 7
    assert optional_bool(d, "missing", default=None) is None

    # Present None returns default
    assert optional_int(d, "n", default=11) == 11


def test_require_list_of_str_validation() -> None:
    """require_list_of_str should validate list elements."""
    d = {"tags": [" a ", "b"]}
    assert require_list_of_str(d, "tags") == ["a", "b"]

    with pytest.raises(ValidationError):
        require_list_of_str({"tags": [1]}, "tags")  # type: ignore[list-item]


def test_require_path_and_optional_path(tmp_path: Path) -> None:
    """Path readers should return Path objects."""
    d = {"p": str(tmp_path / "x.txt")}
    p = require_path(d, "p")
    assert isinstance(p, Path)

    d2 = {"p": None}
    assert optional_path(d2, "p", default=None) is None


def test_net_readers(tmp_path: Path) -> None:
    """Net-related mapping readers should validate host/port/ip/endpoint/url."""
    d = {
        "ip": "10.0.0.1",
        "host": "localhost",
        "port": 8080,
        "endpoint": "localhost:8080",
        "url": "https://example.com/path",
    }
    assert require_ip(d, "ip") == "10.0.0.1"
    assert require_host(d, "host") == "localhost"
    assert require_port(d, "port") == 8080
    assert require_endpoint(d, "endpoint") == ("localhost", 8080)
    assert require_http_url(d, "url") == "https://example.com/path"

    with pytest.raises(ValidationError):
        require_port({"port": 0}, "port")

    with pytest.raises(ValidationError):
        require_http_url({"url": "ftp://example.com"}, "url")
