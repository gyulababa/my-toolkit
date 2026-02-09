# helpers/validation/scalars.py
# Scalar validators (value + path). These functions validate a provided value directly and do NOT read from mappings.

from __future__ import annotations

import ipaddress
import re
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Sequence, TypeVar

from .errors import ValidationError, qpath, type_name

T = TypeVar("T")


def ensure_dict(v: Any, *, path: str = "value") -> dict:
    """Ensure v is a dict."""
    if not isinstance(v, dict):
        raise ValidationError(f"{qpath(path)} must be an object/dict (got {type_name(v)})")
    return v


def ensure_list(v: Any, *, path: str = "value") -> list:
    """Ensure v is a list."""
    if not isinstance(v, list):
        raise ValidationError(f"{qpath(path)} must be a list (got {type_name(v)})")
    return v


def ensure_non_empty_list(v: Any, *, path: str = "value") -> list:
    """Ensure v is a list and has at least 1 element."""
    lst = ensure_list(v, path=path)
    if not lst:
        raise ValidationError(f"{qpath(path)} must be a non-empty list")
    return lst


def ensure_str(v: Any, *, path: str = "value", allow_empty: bool = False) -> str:
    """
    Ensure v is a string.

    Notes:
      - Returns the stripped string.
      - allow_empty=False (default) rejects empty/whitespace-only strings.
    """
    if not isinstance(v, str):
        raise ValidationError(f"{qpath(path)} must be a string (got {type_name(v)})")
    s = v.strip()
    if not allow_empty and not s:
        raise ValidationError(f"{qpath(path)} must be a non-empty string")
    return s


def ensure_bool(v: Any, *, path: str = "value") -> bool:
    """Ensure v is a bool."""
    if not isinstance(v, bool):
        raise ValidationError(f"{qpath(path)} must be a bool (got {type_name(v)})")
    return v


def ensure_int(
    v: Any,
    *,
    path: str = "value",
    min_v: Optional[int] = None,
    max_v: Optional[int] = None,
) -> int:
    """
    Ensure v is an int within optional bounds.

    Note:
      bool is a subclass of int; we explicitly reject bool.
    """
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValidationError(f"{qpath(path)} must be an int (got {type_name(v)})")

    if min_v is not None and v < min_v:
        raise ValidationError(f"{qpath(path)} must be >= {min_v} (got {v})")
    if max_v is not None and v > max_v:
        raise ValidationError(f"{qpath(path)} must be <= {max_v} (got {v})")
    return v


def ensure_float(
    v: Any,
    *,
    path: str = "value",
    min_v: Optional[float] = None,
    max_v: Optional[float] = None,
) -> float:
    """
    Ensure v is a float-like number (int/float) within optional bounds.

    Note:
      bool is rejected.
    """
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValidationError(f"{qpath(path)} must be a float (got {type_name(v)})")

    f = float(v)
    if min_v is not None and f < min_v:
        raise ValidationError(f"{qpath(path)} must be >= {min_v} (got {f})")
    if max_v is not None and f > max_v:
        raise ValidationError(f"{qpath(path)} must be <= {max_v} (got {f})")
    return f


def ensure_one_of(value: Any, allowed: Sequence[Any], *, path: str = "value") -> Any:
    """Ensure value is in allowed."""
    if value not in allowed:
        raise ValidationError(f"{qpath(path)} must be one of {list(allowed)} (got {value!r})")
    return value


def ensure_list_of_dicts(v: Any, *, path: str = "value") -> list[dict]:
    """Ensure v is a list of dicts."""
    lst = ensure_list(v, path=path)
    out: list[dict] = []
    for i, item in enumerate(lst):
        out.append(ensure_dict(item, path=f"{path}[{i}]"))
    return out


def ensure_list_of_str(
    v: Any,
    *,
    path: str = "value",
    allow_empty_items: bool = False,
) -> list[str]:
    """Ensure v is a list of strings (each stripped)."""
    lst = ensure_list(v, path=path)
    out: list[str] = []
    for i, item in enumerate(lst):
        out.append(ensure_str(item, path=f"{path}[{i}]", allow_empty=allow_empty_items))
    return out


def ensure_dict_of_str(
    v: Any,
    *,
    path: str = "value",
    allow_empty_values: bool = False,
) -> dict[str, str]:
    """Ensure v is a dict with string keys and string values (values stripped)."""
    d = ensure_dict(v, path=path)
    out: dict[str, str] = {}
    for k, val in d.items():
        if not isinstance(k, str):
            raise ValidationError(f"{qpath(path)} keys must be strings (got {type_name(k)})")
        out[k] = ensure_str(val, path=f"{path}.{k}", allow_empty=allow_empty_values)
    return out


def ensure_unique(
    items: Iterable[T],
    key_fn: Callable[[T], Any],
    *,
    what: str = "value",
    path: str = "items",
) -> None:
    """Ensure items have unique keys as produced by key_fn()."""
    seen: set[Any] = set()
    for i, item in enumerate(items):
        k = key_fn(item)
        if k in seen:
            raise ValidationError(f"Duplicate {what} '{k}' at {qpath(path)}[{i}]")
        seen.add(k)


def ensure_ip(ip: Any, *, path: str = "ip", version: Optional[int] = None) -> str:
    """
    Ensure an IP address string.

    Parameters:
      ip: expected string like "192.168.0.80" or "fe80::1"
      version:
        - None (default): allow IPv4 or IPv6
        - 4: IPv4 only
        - 6: IPv6 only

    Returns:
      The stripped string.
    """
    s = ensure_str(ip, path=path, allow_empty=False).strip()
    try:
        addr = ipaddress.ip_address(s)
    except ValueError as e:
        raise ValidationError(f"{qpath(path)} must be a valid IP address (got {s!r})") from e

    if version is not None:
        ensure_one_of(version, (4, 6), path=f"{path}.version")
        if addr.version != version:
            raise ValidationError(f"{qpath(path)} must be IPv{version} (got {s!r})")

    return s


def ensure_pathlike(
    v: Any,
    *,
    path: str = "value",
    expanduser: bool = True,
    resolve: bool = False,
) -> Path:
    """
    Ensure v is a path-like value (str or Path) and return a Path.

    Notes:
      - expanduser=True expands "~".
      - resolve=False by default to avoid accidental filesystem coupling and symlink resolution.
    """
    if isinstance(v, Path):
        p = v
    elif isinstance(v, str):
        s = ensure_str(v, path=path, allow_empty=False)
        p = Path(s)
    else:
        raise ValidationError(f"{qpath(path)} must be a path (str or Path) (got {type_name(v)})")

    if expanduser:
        p = p.expanduser()

    return p.resolve() if resolve else p


_ENUM_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def ensure_enum_name(v: Any, *, path: str = "value") -> str:
    """
    Ensure v is a "safe enum name" string.

    Allowed charset:
      A-Z a-z 0-9 _ . -
    """
    s = ensure_str(v, path=path, allow_empty=False)
    if not _ENUM_NAME_RE.match(s):
        raise ValidationError(f"{qpath(path)} must match {_ENUM_NAME_RE.pattern} (got {s!r})")
    return s


def ensure_regex(v: Any, *, path: str = "value") -> re.Pattern[str]:
    """
    Ensure v is a regex pattern string and return a compiled regex.

    Useful for filter rules stored in config/JSON.
    """
    s = ensure_str(v, path=path, allow_empty=False)
    try:
        return re.compile(s)
    except re.error as e:
        raise ValidationError(f"{qpath(path)} must be a valid regex (got {s!r})") from e
