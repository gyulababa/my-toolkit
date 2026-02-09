# helpers/history/history.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional, Union

from .ops import Batch, OpMeta, Operation
from .applier_tree import DocumentApplier
from .paths import get_at, normalize_path_tokens


HistoryEntry = Union[Operation, Batch]


@dataclass
class History:
    applier: DocumentApplier
    # Optional "bound" document reference for convenience helpers.
    # If you prefer purely functional usage, ignore this and use apply()/undo()/redo() directly.
    doc: Any = None
    undo_stack: List[HistoryEntry] = field(default_factory=list)
    redo_stack: List[HistoryEntry] = field(default_factory=list)

    _open_batch_label: Optional[str] = None
    _open_batch_ops: List[Operation] = field(default_factory=list)

    def begin_batch(self, label: str = "") -> None:
        if self._open_batch_label is not None:
            raise RuntimeError("Batch already open")
        self._open_batch_label = label
        self._open_batch_ops = []

    def end_batch(self) -> None:
        if self._open_batch_label is None:
            raise RuntimeError("No open batch")
        if self._open_batch_ops:
            self.undo_stack.append(Batch(label=self._open_batch_label, ops=tuple(self._open_batch_ops)))
            self.redo_stack.clear()
        self._open_batch_label = None
        self._open_batch_ops = []

    def apply(self, doc: Any, op: Operation) -> Any:
        # Apply mutation
        doc = self.applier.apply(doc, op)
        self.doc = doc

        # Record
        if self._open_batch_label is not None:
            self._open_batch_ops.append(op)
        else:
            # Coalesce: if last op has same coalesce_key, update last.after
            if op.coalesce_key and self.undo_stack:
                last = self.undo_stack[-1]
                if isinstance(last, Operation) and last.coalesce_key == op.coalesce_key:
                    # Replace last op with merged 'after'
                    merged = Operation(
                        patch_type=last.patch_type,
                        path=last.path,
                        before=last.before,
                        after=op.after,
                        index=op.index,
                        from_index=op.from_index,
                        to_index=op.to_index,
                        coalesce_key=last.coalesce_key,
                        meta=op.meta,
                    )
                    self.undo_stack[-1] = merged
                    self.redo_stack.clear()
                    return doc

            self.undo_stack.append(op)
            self.redo_stack.clear()

        return doc

    def undo(self, doc: Any) -> Any:
        if not self.undo_stack:
            return doc
        entry = self.undo_stack.pop()

        if isinstance(entry, Batch):
            # Undo in reverse order
            for op in reversed(entry.ops):
                inv = self.applier.invert(op)
                doc = self.applier.apply(doc, inv)
            self.redo_stack.append(entry)
            self.doc = doc
            return doc

        inv = self.applier.invert(entry)
        doc = self.applier.apply(doc, inv)
        self.redo_stack.append(entry)
        self.doc = doc
        return doc

    def redo(self, doc: Any) -> Any:
        if not self.redo_stack:
            return doc
        entry = self.redo_stack.pop()

        if isinstance(entry, Batch):
            for op in entry.ops:
                doc = self.applier.apply(doc, op)
            self.undo_stack.append(entry)
            self.doc = doc
            return doc

        doc = self.applier.apply(doc, entry)
        self.undo_stack.append(entry)
        self.doc = doc
        return doc

    def clear(self) -> None:
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._open_batch_label = None
        self._open_batch_ops = []

    # -------------------------
    # Universal convenience helpers (path-based)
    # -------------------------
    def _require_doc(self) -> Any:
        if self.doc is None:
            raise RuntimeError(
                "History.doc is not set. Call history.apply(...), history.undo(...), "
                "history.redo(...), or assign history.doc before using push_* helpers."
            )
        return self.doc

    def push_list_append(self, path: Union[str, list[Any]], item: Any) -> Any:
        """Append to a list at path by recording+applying an insert operation."""
        doc = self._require_doc()
        p = normalize_path_tokens(path)
        lst = get_at(doc, p)
        if not isinstance(lst, list):
            raise TypeError(f"push_list_append requires list at {p}, got {type(lst).__name__}")

        op = Operation(
            patch_type="insert",
            path=p,
            before=None,
            after=item,
            index=len(lst),
            meta=OpMeta(source="history", reason="push_list_append"),
        )
        return self.apply(doc, op)

    def push_list_remove(self, path: Union[str, list[Any]], index: int) -> Any:
        """Remove an item from a list at path by recording+applying a remove operation."""
        doc = self._require_doc()
        p = normalize_path_tokens(path)
        lst = get_at(doc, p)
        if not isinstance(lst, list):
            raise TypeError(f"push_list_remove requires list at {p}, got {type(lst).__name__}")
        if index < 0 or index >= len(lst):
            raise IndexError(index)

        removed = lst[index]
        op = Operation(
            patch_type="remove",
            path=p,
            before=removed,
            after=None,
            index=index,
            meta=OpMeta(source="history", reason="push_list_remove"),
        )
        return self.apply(doc, op)

    def push_set(self, path: Union[str, list[Any]], old: Any, new: Any) -> Any:
        """Set a value at path by recording+applying a set operation."""
        doc = self._require_doc()
        p = normalize_path_tokens(path)

        cur = get_at(doc, p)
        if cur != old:
            raise ValueError(f"push_set old mismatch at {p}: expected {old!r}, found {cur!r}")

        op = Operation(
            patch_type="set",
            path=p,
            before=old,
            after=new,
            meta=OpMeta(source="history", reason="push_set"),
        )
        return self.apply(doc, op)
