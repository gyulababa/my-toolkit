# helpers/history/paths.py
from __future__ import annotations

from typing import Any, List, Sequence, Union


PathToken = Union[str, int]
Path = List[PathToken]


class PathError(Exception):
    """Raised when a document path is invalid for the current document shape."""


def normalize_path_tokens(path: Sequence[PathToken] | str) -> Path:
    """
    Normalize a user-facing path representation into a list of tokens.

    Accepted inputs:
      - list/tuple of tokens: ["a", "b", 0]
      - dotted string path: "a.b.c" (string tokens only)

    Notes:
      - Dotted string paths do not support integer tokens.
      - Tokens are *not* validated against a document here.
    """
    if isinstance(path, str):
        if path == "":
            return []
        return [tok for tok in path.split(".") if tok != ""]
    return list(path)


def _expect_dict(obj: Any, path: Path) -> dict:
    if not isinstance(obj, dict):
        raise PathError(f"Expected dict at path {path}, got {type(obj).__name__}")
    return obj


def _expect_list(obj: Any, path: Path) -> list:
    if not isinstance(obj, list):
        raise PathError(f"Expected list at path {path}, got {type(obj).__name__}")
    return obj


def exists_at(doc: Any, path: Sequence[PathToken] | str) -> bool:
    """Return True if the path can be fully resolved in the document."""
    try:
        _ = get_at(doc, path)
        return True
    except Exception:
        return False


def get_at(doc: Any, path: Sequence[PathToken] | str) -> Any:
    """Resolve the value at path. Raises if any token cannot be resolved."""
    p = normalize_path_tokens(path)
    cur = doc
    for tok in p:
        if isinstance(tok, int):
            cur = _expect_list(cur, p)[tok]
        else:
            cur = _expect_dict(cur, p)[tok]
    return cur


def set_at(doc: Any, path: Sequence[PathToken] | str, value: Any) -> Any:
    """
    Set a value at path.

    Semantics:
      - Empty path means root replacement (returns value).
      - For dict keys, the key must exist (KeyError if missing).
      - For list indices, the index must be in range (IndexError if invalid).
    """
    p = normalize_path_tokens(path)
    if not p:
        return value

    cur = doc
    for tok in p[:-1]:
        if isinstance(tok, int):
            cur = _expect_list(cur, p)[tok]
        else:
            cur = _expect_dict(cur, p)[tok]

    last = p[-1]
    if isinstance(last, int):
        _expect_list(cur, p)[last] = value
    else:
        _expect_dict(cur, p)[last] = value
    return doc


def del_at(doc: Any, path: Sequence[PathToken] | str) -> Any:
    """
    Delete a dict key at path.

    Design choice (to keep inversion semantics predictable):
      - Only supports deleting dict keys (last token must be str).
      - Missing key is a no-op.
      - Empty path is invalid.
    """
    p = normalize_path_tokens(path)
    if not p:
        raise PathError("del_at requires non-empty path")

    last = p[-1]
    if not isinstance(last, str):
        raise PathError(f"del_at requires last token to be str key, got {type(last).__name__}")

    parent_path = p[:-1]
    parent = get_at(doc, parent_path) if parent_path else doc
    parent_dict = _expect_dict(parent, p)
    parent_dict.pop(last, None)
    return doc


def ensure_container_at(doc: Any, path: Sequence[PathToken] | str, kind: str) -> Any:
    """
    Resolve a container at path and validate its type.

    This helper intentionally does *not* create missing containers.
    """
    cur = get_at(doc, path)
    p = normalize_path_tokens(path)
    if kind == "list":
        return _expect_list(cur, p)
    if kind == "dict":
        return _expect_dict(cur, p)
    raise ValueError(f"Unknown container kind: {kind}")
