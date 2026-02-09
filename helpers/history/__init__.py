# helpers/history/__init__.py
# Public exports for helpers.history (undo/redo, operations, and tree applier utilities).

"""
helpers.history

Undo/redo and patch application helpers.

This package provides:
  - Operation and Batch types (ops.py)
  - Tree path get/set/del utilities (paths.py)
  - TreeApplier and ImmutableTreeApplier for dict/list documents (applier_tree.py)
  - History stack (history.py)
"""

from .ops import Operation, Batch, Path, PathToken, OpMeta
from .paths import PathError, del_at, exists_at, get_at, set_at
from .applier_tree import DocumentApplier, ImmutableTreeApplier, TreeApplier
from .history import History, HistoryEntry

__all__ = [
    # ops
    "Operation",
    "Batch",
    "OpMeta",
    "Path",
    "PathToken",
    # applier + history
    "History",
    "HistoryEntry",
    "DocumentApplier",
    "TreeApplier",
    "ImmutableTreeApplier",
    # paths
    "PathError",
    "get_at",
    "set_at",
    "del_at",
    "exists_at",
]
