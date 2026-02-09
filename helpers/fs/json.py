# helpers/fs/json.py
# JSON helpers built on text IO and atomic writes: read/write, defaults, strict reads, compact writes, and transactional updates.

from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Callable

from .dirs import ensure_parent
from .text import read_text
from .atomic import atomic_write_text


def read_json(path: str | Path, *, encoding: str = "utf-8") -> Any:
    """
    Read JSON from a file and return the decoded object.

    Notes:
      - Raises JSONDecodeError if the file content is not valid JSON.
      - If the file is empty/whitespace, JSON decoding will fail; use read_json_default(..., allow_empty=True)
        if you want to treat empty as a default value.
    """
    p = Path(path)
    s = read_text(p, encoding=encoding)

    try:
        return json.loads(s)
    except JSONDecodeError as e:
        # Common case: empty file (or whitespace-only)
        if s.strip() == "":
            raise JSONDecodeError(
                f"Empty/whitespace-only JSON file: {p}",
                s,
                0,
            ) from e
        # Otherwise bubble up with original details; callers can catch JSONDecodeError.
        raise


def read_json_default(
    path: str | Path,
    default: Any,
    *,
    encoding: str = "utf-8",
    allow_empty: bool = False,
) -> Any:
    """
    Read JSON from a file, returning default if the file does not exist.

    Args:
      allow_empty:
        If True and the file exists but is empty/whitespace-only, return default.
        Useful for state/cache files that may be created before data is written.
    """
    p = Path(path)
    if not p.exists():
        return default

    if allow_empty:
        s = read_text(p, encoding=encoding)
        if s.strip() == "":
            return default
        return json.loads(s)

    return read_json(p, encoding=encoding)


def read_json_strict(
    path: str | Path,
    *,
    encoding: str = "utf-8",
    root_types: tuple[type, ...] = (dict, list),
    allow_empty: bool = False,
    empty_default: Any = None,
) -> Any:
    """
    Read JSON and enforce the decoded root type.

    Args:
      root_types: tuple of allowed root types, default (dict, list).
      allow_empty:
        If True and the file exists but is empty/whitespace-only, return empty_default.
      empty_default:
        Value returned when allow_empty=True and file is empty. If None, defaults to {}.
    """
    if allow_empty:
        if empty_default is None:
            empty_default = {}
        obj = read_json_default(path, empty_default, encoding=encoding, allow_empty=True)
    else:
        obj = read_json(path, encoding=encoding)

    if not isinstance(obj, root_types):
        allowed = ", ".join(t.__name__ for t in root_types)
        raise TypeError(f"JSON root type must be one of: {allowed}")
    return obj


def write_json(
    path: str | Path,
    data: Any,
    *,
    encoding: str = "utf-8",
    indent: int = 2,
    sort_keys: bool = True,
) -> None:
    """
    Write JSON to a file (non-atomic), creating parent directories if needed.

    If you need crash-safe writes, prefer atomic_write_json().
    """
    p = Path(path)
    ensure_parent(p)
    p.write_text(
        json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=False),
        encoding=encoding,
    )


def write_json_compact(
    path: str | Path,
    data: Any,
    *,
    encoding: str = "utf-8",
    sort_keys: bool = True,
) -> None:
    """
    Write JSON to a file in a compact form (no extra whitespace).

    Useful for caches or artifacts where readability is not important.
    """
    p = Path(path)
    ensure_parent(p)
    p.write_text(
        json.dumps(data, sort_keys=sort_keys, ensure_ascii=False, separators=(",", ":")),
        encoding=encoding,
    )


def atomic_write_json(
    path: str | Path,
    data: Any,
    *,
    encoding: str = "utf-8",
    indent: int = 2,
    sort_keys: bool = True,
    overwrite: bool = True,
) -> None:
    """
    Atomically write JSON to a file.

    Uses atomic_write_text() under the hood. Recommended for:
    - user-edited config files
    - app state files
    - caches that should not end up half-written
    """
    payload = json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
    atomic_write_text(path, payload, encoding=encoding, overwrite=overwrite)


def update_json(
    path: str | Path,
    mutator: Callable[[Any], Any] | Callable[[Any], None],
    *,
    encoding: str = "utf-8",
    atomic: bool = True,
    indent: int = 2,
    sort_keys: bool = True,
    default: Any = None,
) -> Any:
    """
    Transaction-style JSON update: read -> mutate -> write (optionally atomic).

    Args:
      mutator:
        A function called with the decoded JSON object.
        - If it returns a value other than None, that value becomes the new object.
        - If it returns None, the object is assumed to be modified in-place.
      default:
        Value used if the file does not exist. If None, defaults to {}.

    Returns:
      The updated object that was written.
    """
    if default is None:
        default = {}

    # For transactional updates, treating an empty file as "no state yet" is typically desirable.
    obj = read_json_default(path, default, encoding=encoding, allow_empty=True)

    res = mutator(obj)
    if res is not None:
        obj = res

    if atomic:
        atomic_write_json(path, obj, encoding=encoding, indent=indent, sort_keys=sort_keys)
    else:
        write_json(path, obj, encoding=encoding, indent=indent, sort_keys=sort_keys)
    return obj
