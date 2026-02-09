# helpers/validation/mapping.py
# Mapping readers (mapping + key + path). These functions read a field and validate it using scalar validators.

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional, Sequence, TypeVar

from .errors import ValidationError, qpath
from .net import _require_ip_value, ensure_endpoint, ensure_host, ensure_http_url, ensure_port
from .scalars import (
    ensure_bool,
    ensure_dict,
    ensure_dict_of_str,
    ensure_float,
    ensure_int,
    ensure_list,
    ensure_list_of_dicts,
    ensure_list_of_str,
    ensure_one_of,
    ensure_pathlike,
    ensure_regex,
    ensure_str,
)

T = TypeVar("T")

# Sentinel used to distinguish:
#   "key not provided"  vs  "key provided with value None"
_MISSING = object()


def path_join(path: str, key: str) -> str:
    """
    Join a parent path and a key into a dotted path.

    Examples:
      path_join("strip", "led_count") -> "strip.led_count"
      path_join("", "controllers")    -> "controllers"
    """
    return f"{path}.{key}" if path else key


def _get_value(d: Mapping[str, Any], key: str, *, path: str, default: Any) -> Any:
    """
    Common retrieval semantics:
      - if key missing and default is _MISSING -> raise required error
      - if key missing and default provided -> return default
      - else return d[key]
    """
    p = path_join(path, key) if path else key
    if key not in d:
        if default is _MISSING:
            raise ValidationError(f"Missing required field {qpath(p)}")
        return default
    return d[key]


# -------------------------
# Backwards-compatible aliases
# -------------------------

def require_dict(v: Any, *, path: str = "value") -> dict:
    """Backwards-compatible alias; delegates to ensure_dict()."""
    return ensure_dict(v, path=path)


def require_list(v: Any, *, path: str = "value") -> list:
    """Backwards-compatible alias; delegates to ensure_list()."""
    return ensure_list(v, path=path)


# -------------------------
# Required field readers
# -------------------------

def require_str(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    allow_empty: bool = False,
    default: Any = _MISSING,
) -> str:
    """Read d[key] as a validated string."""
    p = path_join(path, key) if path else key
    v = _get_value(d, key, path=path, default=default)
    return ensure_str(v, path=p, allow_empty=allow_empty)


def require_int(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    min_v: Optional[int] = None,
    max_v: Optional[int] = None,
    default: Any = _MISSING,
) -> int:
    """Read d[key] as a validated int."""
    p = path_join(path, key) if path else key
    v = _get_value(d, key, path=path, default=default)
    return ensure_int(v, path=p, min_v=min_v, max_v=max_v)


def require_float(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    min_v: Optional[float] = None,
    max_v: Optional[float] = None,
    default: Any = _MISSING,
) -> float:
    """Read d[key] as a validated float."""
    p = path_join(path, key) if path else key
    v = _get_value(d, key, path=path, default=default)
    return ensure_float(v, path=p, min_v=min_v, max_v=max_v)


def require_bool(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    default: Any = _MISSING,
) -> bool:
    """Read d[key] as a validated bool."""
    p = path_join(path, key) if path else key
    v = _get_value(d, key, path=path, default=default)
    return ensure_bool(v, path=p)


def require_list_of_dicts(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    default: Any = _MISSING,
) -> list[dict]:
    """Read d[key] as a list of dicts."""
    p = path_join(path, key) if path else key
    v = _get_value(d, key, path=path, default=default)
    return ensure_list_of_dicts(v, path=p)


def require_list_of_str(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    allow_empty_items: bool = False,
    default: Any = _MISSING,
) -> list[str]:
    """Read d[key] as a list of strings."""
    p = path_join(path, key) if path else key
    v = _get_value(d, key, path=path, default=default)
    return ensure_list_of_str(v, path=p, allow_empty_items=allow_empty_items)


def require_dict_of_str(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    allow_empty_values: bool = False,
    default: Any = _MISSING,
) -> dict[str, str]:
    """Read d[key] as a dict[str, str]."""
    p = path_join(path, key) if path else key
    v = _get_value(d, key, path=path, default=default)
    return ensure_dict_of_str(v, path=p, allow_empty_values=allow_empty_values)


def require_one_of(
    d: Mapping[str, Any],
    key: str,
    allowed: Sequence[Any],
    *,
    path: str = "",
    default: Any = _MISSING,
) -> Any:
    """Read d[key] and ensure it is in allowed."""
    p = path_join(path, key) if path else key
    v = _get_value(d, key, path=path, default=default)
    return ensure_one_of(v, allowed, path=p)


def require_path(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    expanduser: bool = True,
    resolve: bool = False,
    default: Any = _MISSING,
) -> Path:
    """Read d[key] as a Path-like value and return a Path."""
    p = path_join(path, key) if path else key
    v = _get_value(d, key, path=path, default=default)
    return ensure_pathlike(v, path=p, expanduser=expanduser, resolve=resolve)


def require_regex(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    default: Any = _MISSING,
):
    """Read d[key] as a regex pattern string and return compiled regex."""
    p = path_join(path, key) if path else key
    v = _get_value(d, key, path=path, default=default)
    return ensure_regex(v, path=p)


def require_ip(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    version: Optional[int] = None,
    default: Any = _MISSING,
) -> str:
    """Read d[key] as an IP address string."""
    p = path_join(path, key) if path else key
    v = _get_value(d, key, path=path, default=default)
    # _require_ip_value expects an already-joined path string; we pass p.
    return _require_ip_value(v, p=p, version=version)


def require_port(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    default: Any = _MISSING,
) -> int:
    """Read d[key] as a TCP/UDP port (1..65535)."""
    p = path_join(path, key) if path else key
    v = _get_value(d, key, path=path, default=default)
    return ensure_port(v, path=p)


def require_host(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    allow_localhost: bool = True,
    default: Any = _MISSING,
) -> str:
    """Read d[key] as a host (hostname or IP)."""
    p = path_join(path, key) if path else key
    v = _get_value(d, key, path=path, default=default)
    return ensure_host(v, path=p, allow_localhost=allow_localhost)


def require_endpoint(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    default: Any = _MISSING,
) -> tuple[str, int]:
    """Read d[key] as an endpoint string and return (host, port)."""
    p = path_join(path, key) if path else key
    v = _get_value(d, key, path=path, default=default)
    return ensure_endpoint(v, path=p)


def require_http_url(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    default: Any = _MISSING,
) -> str:
    """Read d[key] as an http(s) URL."""
    p = path_join(path, key) if path else key
    v = _get_value(d, key, path=path, default=default)
    return ensure_http_url(v, path=p)


# -------------------------
# Optional field readers
# -------------------------

def optional_str(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    allow_empty: bool = False,
    default: Optional[str] = None,
) -> Optional[str]:
    """Optional string reader: returns default if missing or None."""
    p = path_join(path, key) if path else key
    if key not in d or d[key] is None:
        return default
    return ensure_str(d[key], path=p, allow_empty=allow_empty)


def optional_int(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    min_v: Optional[int] = None,
    max_v: Optional[int] = None,
    default: Optional[int] = None,
) -> Optional[int]:
    """Optional int reader: returns default if missing or None."""
    p = path_join(path, key) if path else key
    if key not in d or d[key] is None:
        return default
    return ensure_int(d[key], path=p, min_v=min_v, max_v=max_v)


def optional_float(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    min_v: Optional[float] = None,
    max_v: Optional[float] = None,
    default: Optional[float] = None,
) -> Optional[float]:
    """Optional float reader: returns default if missing or None."""
    p = path_join(path, key) if path else key
    if key not in d or d[key] is None:
        return default
    return ensure_float(d[key], path=p, min_v=min_v, max_v=max_v)


def optional_bool(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    default: Optional[bool] = None,
) -> Optional[bool]:
    """Optional bool reader: returns default if missing or None."""
    p = path_join(path, key) if path else key
    if key not in d or d[key] is None:
        return default
    return ensure_bool(d[key], path=p)


def optional_list_of_str(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    allow_empty_items: bool = False,
    default: Optional[list[str]] = None,
) -> Optional[list[str]]:
    """Optional list[str] reader: returns default if missing or None."""
    p = path_join(path, key) if path else key
    if key not in d or d[key] is None:
        return default
    return ensure_list_of_str(d[key], path=p, allow_empty_items=allow_empty_items)


def optional_path(
    d: Mapping[str, Any],
    key: str,
    *,
    path: str = "",
    expanduser: bool = True,
    resolve: bool = False,
    default: Optional[Path] = None,
) -> Optional[Path]:
    """Optional path reader: returns default if missing or None."""
    p = path_join(path, key) if path else key
    if key not in d or d[key] is None:
        return default
    return ensure_pathlike(d[key], path=p, expanduser=expanduser, resolve=resolve)
