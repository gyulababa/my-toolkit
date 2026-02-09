# helpers/history/ops.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Union
import time
import uuid


PathToken = Union[str, int]
Path = List[PathToken]


@dataclass(frozen=True)
class OpMeta:
    ts: float = field(default_factory=lambda: time.time())
    actor: str = "user"
    source: str = "unknown"  # e.g. "ui/dearpygui", "cli", "api"
    reason: str = ""         # e.g. "drag", "typing", "import"
    note: str = ""           # free text
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Operation:
    """
    Universal, invertible mutation.

    patch_type:
      - "set": replace value at path
      - "merge": shallow-merge dict at path
      - "insert": insert into list at (path -> list), index given
      - "remove": remove from list at (path -> list), index given
      - "move": move element inside list at (path -> list)
      - "replace": replace subtree at path (same as set, but semantic)
    """
    patch_type: str
    path: Path

    # Values required for inversion
    before: Any
    after: Any

    # Optional parameters for list ops
    index: Optional[int] = None
    from_index: Optional[int] = None
    to_index: Optional[int] = None

    # Coalescing key: if last op shares key, history can replace last.after
    coalesce_key: Optional[str] = None

    # Identity / metadata
    op_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    meta: OpMeta = field(default_factory=OpMeta)


@dataclass(frozen=True)
class Batch:
    """
    A group of operations treated as one undo/redo step.
    """
    label: str = ""
    ops: Sequence[Operation] = field(default_factory=list)
    batch_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    meta: OpMeta = field(default_factory=OpMeta)
