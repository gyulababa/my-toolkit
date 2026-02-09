# helpers/history/applier_tree.py
# Operation applier for dict/list/primitive documents. Implements apply() and invert() for the Operation protocol.
# Includes both mutable (TreeApplier) and immutable (ImmutableTreeApplier) strategies.

from __future__ import annotations

from dataclasses import replace
from typing import Any, Protocol

from .ops import Operation
from .paths import (
    PathError,
    del_at,
    ensure_container_at,
    get_at,
    normalize_path_tokens,
    set_at,
)


class DocumentApplier(Protocol):
    """
    Strategy interface for applying/inverting operations on a document model.

    This allows swapping TreeApplier for domain-specific appliers later
    (e.g. stricter type enforcement or immutable update strategies).
    """

    def apply(self, doc: Any, op: Operation) -> Any: ...
    def invert(self, op: Operation) -> Operation: ...


class TreeApplier:
    """
    Applies operations to documents composed of dict/list/primitive nodes (MUTABLE strategy).

    Semantics:
      - "set"/"replace"/"merge" return a (potentially new) root when path is empty.
      - list operations ("insert"/"remove"/"move") mutate the list in-place and return the same root.
      - "del" deletes a dict key (no-op if missing).
    """

    def apply(self, doc: Any, op: Operation) -> Any:
        path = normalize_path_tokens(op.path)
        t = op.patch_type

        if t in ("set", "replace"):
            return set_at(doc, path, op.after)

        if t == "merge":
            cur = get_at(doc, path)
            if not isinstance(cur, dict) or not isinstance(op.after, dict):
                raise PathError(f"merge requires dict at {path}")
            merged = dict(cur)
            merged.update(op.after)
            return set_at(doc, path, merged)

        if t == "insert":
            if op.index is None:
                raise ValueError("insert requires index")
            lst = ensure_container_at(doc, path, "list")
            lst.insert(op.index, op.after)
            return doc

        if t == "remove":
            if op.index is None:
                raise ValueError("remove requires index")
            lst = ensure_container_at(doc, path, "list")
            lst.pop(op.index)
            return doc

        if t == "move":
            if op.from_index is None or op.to_index is None:
                raise ValueError("move requires from_index and to_index")
            lst = ensure_container_at(doc, path, "list")
            item = lst.pop(op.from_index)
            lst.insert(op.to_index, item)
            return doc

        if t == "del":
            return del_at(doc, path)

        raise ValueError(f"Unknown patch_type: {t}")

    def invert(self, op: Operation) -> Operation:
        if op.patch_type == "move":
            return replace(
                op,
                from_index=op.to_index,
                to_index=op.from_index,
                before=op.after,
                after=op.before,
            )

        if op.patch_type == "insert":
            return replace(op, patch_type="remove", before=op.after, after=op.before)

        if op.patch_type == "remove":
            return replace(op, patch_type="insert", before=op.after, after=op.before)

        if op.patch_type == "del":
            return replace(op, patch_type="set", before=None, after=op.before)

        return replace(op, before=op.after, after=op.before)


def _cow_set_at(doc: Any, path: list[Any], value: Any) -> Any:
    """
    Copy-on-write set_at.

    Returns:
      A new root object with copies along the path. Unchanged subtrees are shared.

    Rules:
      - If path is empty, returns value (root replacement).
      - For dict/list containers on the path, shallow-copies are made.
      - Type mismatch raises PathError.
    """
    if not path:
        return value

    # Recursive copy-on-write
    tok = path[0]
    rest = path[1:]

    if isinstance(tok, int):
        if not isinstance(doc, list):
            raise PathError(f"Expected list at path {path}, got {type(doc).__name__}")
        if tok < 0 or tok >= len(doc):
            raise IndexError(tok)
        new_list = list(doc)
        new_list[tok] = _cow_set_at(doc[tok], rest, value)
        return new_list

    # str key
    if not isinstance(doc, dict):
        raise PathError(f"Expected dict at path {path}, got {type(doc).__name__}")
    if tok not in doc:
        raise KeyError(tok)
    new_dict = dict(doc)
    new_dict[tok] = _cow_set_at(doc[tok], rest, value)
    return new_dict


def _cow_del_at(doc: Any, path: list[Any]) -> Any:
    """
    Copy-on-write delete.

    Semantics:
      - Empty path: error (cannot delete root)
      - Dict last token: delete key if present (no-op if missing)
      - List last token: delete index (IndexError if out of range)
    """
    if not path:
        raise PathError("del_at requires non-empty path")

    if len(path) == 1:
        key = path[0]
        if isinstance(key, int):
            if not isinstance(doc, list):
                raise PathError(f"Expected list at path {path}, got {type(doc).__name__}")
            new_list = list(doc)
            del new_list[key]
            return new_list

        if not isinstance(doc, dict):
            raise PathError(f"Expected dict at path {path}, got {type(doc).__name__}")
        new_dict = dict(doc)
        new_dict.pop(key, None)
        return new_dict

    tok = path[0]
    rest = path[1:]

    if isinstance(tok, int):
        if not isinstance(doc, list):
            raise PathError(f"Expected list at path {path}, got {type(doc).__name__}")
        if tok < 0 or tok >= len(doc):
            raise IndexError(tok)
        new_list = list(doc)
        new_list[tok] = _cow_del_at(doc[tok], rest)
        return new_list

    if not isinstance(doc, dict):
        raise PathError(f"Expected dict at path {path}, got {type(doc).__name__}")
    if tok not in doc:
        raise KeyError(tok)
    new_dict = dict(doc)
    new_dict[tok] = _cow_del_at(doc[tok], rest)
    return new_dict


def _cow_list_insert(doc: Any, path: list[Any], index: int, value: Any) -> Any:
    """Copy-on-write list insert at a list located by path."""
    lst = get_at(doc, path)
    if not isinstance(lst, list):
        raise PathError(f"Expected list at path {path}, got {type(lst).__name__}")
    new_list = list(lst)
    new_list.insert(index, value)
    return _cow_set_at(doc, path, new_list)


def _cow_list_remove(doc: Any, path: list[Any], index: int) -> Any:
    """Copy-on-write list remove at a list located by path."""
    lst = get_at(doc, path)
    if not isinstance(lst, list):
        raise PathError(f"Expected list at path {path}, got {type(lst).__name__}")
    new_list = list(lst)
    new_list.pop(index)
    return _cow_set_at(doc, path, new_list)


def _cow_list_move(doc: Any, path: list[Any], from_index: int, to_index: int) -> Any:
    """Copy-on-write list move inside a list located by path."""
    lst = get_at(doc, path)
    if not isinstance(lst, list):
        raise PathError(f"Expected list at path {path}, got {type(lst).__name__}")
    new_list = list(lst)
    item = new_list.pop(from_index)
    new_list.insert(to_index, item)
    return _cow_set_at(doc, path, new_list)


class ImmutableTreeApplier(TreeApplier):
    """
    Copy-on-write variant of TreeApplier.

    Use this when:
      - you keep snapshots of doc across time
      - you want to avoid shared mutable references after apply()
      - you want "functional" semantics for updates

    Tradeoffs:
      - slower than TreeApplier for deep paths (copies along the path)
      - but predictable and safe for UI state/time-travel.
    """

    def apply(self, doc: Any, op: Operation) -> Any:
        path = normalize_path_tokens(op.path)
        t = op.patch_type

        if t in ("set", "replace"):
            return _cow_set_at(doc, path, op.after)

        if t == "merge":
            cur = get_at(doc, path)
            if not isinstance(cur, dict) or not isinstance(op.after, dict):
                raise PathError(f"merge requires dict at {path}")
            merged = dict(cur)
            merged.update(op.after)
            return _cow_set_at(doc, path, merged)

        if t == "insert":
            if op.index is None:
                raise ValueError("insert requires index")
            return _cow_list_insert(doc, path, op.index, op.after)

        if t == "remove":
            if op.index is None:
                raise ValueError("remove requires index")
            return _cow_list_remove(doc, path, op.index)

        if t == "move":
            if op.from_index is None or op.to_index is None:
                raise ValueError("move requires from_index and to_index")
            return _cow_list_move(doc, path, op.from_index, op.to_index)

        if t == "del":
            return _cow_del_at(doc, path)

        raise ValueError(f"Unknown patch_type: {t}")
