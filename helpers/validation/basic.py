# helpers/validation/basic.py
# Backwards-compatible façade. Re-exports the "legacy" API surface while delegating implementation to focused modules.

from __future__ import annotations

from .errors import ValidationError, qpath, type_name as _type_name
from .mapping import (
    path_join as _path_join,
    require_bool,
    require_dict,
    require_dict_of_str,
    require_endpoint,
    require_float,
    require_host,
    require_http_url,
    require_int,
    require_ip,
    require_list,
    require_list_of_dicts,
    require_list_of_str,
    require_path,
    require_port,
    require_regex,
    require_str,
    optional_bool,
    optional_float,
    optional_int,
    optional_list_of_str,
    optional_path,
    optional_str,
)
from .net import ensure_endpoint, ensure_host, ensure_http_url, ensure_port
from .scalars import (
    ensure_bool,
    ensure_dict,
    ensure_dict_of_str,
    ensure_enum_name,
    ensure_float,
    ensure_int,
    ensure_ip,
    ensure_list,
    ensure_list_of_dicts,
    ensure_list_of_str,
    ensure_non_empty_list,
    ensure_one_of,
    ensure_pathlike,
    ensure_regex,
    ensure_str,
    ensure_unique,
)

# Keep sentinel name for compatibility (rare, but safe)
from .mapping import _MISSING  # type: ignore

__all__ = [
    # errors
    "ValidationError",
    # legacy helpers (historical)
    "qpath",
    # scalar validators
    "ensure_dict",
    "ensure_list",
    "ensure_non_empty_list",
    "ensure_str",
    "ensure_bool",
    "ensure_int",
    "ensure_float",
    "ensure_one_of",
    "ensure_list_of_dicts",
    "ensure_list_of_str",
    "ensure_dict_of_str",
    "ensure_unique",
    "ensure_ip",
    "ensure_pathlike",
    "ensure_enum_name",
    "ensure_regex",
    # mapping readers
    "require_dict",
    "require_list",
    "require_str",
    "require_int",
    "require_float",
    "require_bool",
    "require_list_of_dicts",
    "require_list_of_str",
    "require_dict_of_str",
    "require_one_of",
    "require_unique",
    "require_path",
    "require_regex",
    "require_ip",
    "require_port",
    "require_host",
    "require_endpoint",
    "require_http_url",
    # optional readers
    "optional_str",
    "optional_int",
    "optional_float",
    "optional_bool",
    "optional_list_of_str",
    "optional_path",
    # net validators
    "ensure_port",
    "ensure_host",
    "ensure_endpoint",
    "ensure_http_url",
    # internal (compat)
    "_MISSING",
]


def require_unique(
    items,
    key_fn,
    *,
    what: str = "value",
    path: str = "items",
) -> None:
    return ensure_unique(items, key_fn, what=what, path=path)


def require_one_of(value, allowed, *, path: str = "value"):
    return ensure_one_of(value, allowed, path=path)
