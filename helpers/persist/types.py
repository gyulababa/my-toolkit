# helpers/persist/types.py
# Persist-layer datatypes: index state, history metadata, and doc/domain reporting types for UIs and diagnostics.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class PersistHistoryEntry:
    """
    Optional index history item.

    This is intentionally lightweight and not relied upon for correctness.
    It is meant for user-visible audit trails or debugging.
    """
    doc_id: str
    created_at: str
    note: Optional[str] = None

    def to_raw(self) -> Dict[str, Any]:
        """Serialize to a JSON-compatible dict."""
        raw: Dict[str, Any] = {
            "doc_id": self.doc_id,
            "created_at": self.created_at,
        }
        if self.note is not None:
            raw["note"] = self.note
        return raw

    @staticmethod
    def from_raw(raw: Dict[str, Any]) -> "PersistHistoryEntry":
        """Deserialize from a JSON-compatible dict."""
        return PersistHistoryEntry(
            doc_id=str(raw.get("doc_id", "")),
            created_at=str(raw.get("created_at", "")),
            note=raw.get("note", None),
        )


@dataclass
class PersistIndex:
    """
    Domain-level persist index.

    Fields:
      active_id:
        The doc_id considered "active" (e.g., the one the app should load by default).
      next_id:
        Next numeric id to allocate. Doc ids are formatted as 4 digits (0001, 0002, ...).
      history:
        Optional list of history entries (not required for correctness).
    """
    active_id: str = "0001"
    next_id: int = 2
    history: List[PersistHistoryEntry] = field(default_factory=list)

    def to_raw(self) -> Dict[str, Any]:
        """Serialize to a JSON-compatible dict."""
        return {
            "active_id": self.active_id,
            "next_id": self.next_id,
            "history": [h.to_raw() for h in self.history],
        }

    @staticmethod
    def from_raw(raw: Dict[str, Any]) -> "PersistIndex":
        """Deserialize from a JSON-compatible dict."""
        active_id = str(raw.get("active_id", "0001"))
        next_id = int(raw.get("next_id", 2))

        hist_raw = raw.get("history", [])
        history: List[PersistHistoryEntry] = []
        if isinstance(hist_raw, list):
            for item in hist_raw:
                if isinstance(item, dict):
                    history.append(PersistHistoryEntry.from_raw(item))

        return PersistIndex(active_id=active_id, next_id=next_id, history=history)


@dataclass(frozen=True)
class PersistDocInfo:
    """
    Persisted document inventory information (useful for UIs and tooling).

    Notes:
      - mtime_iso is UTC ISO8601 when available.
      - size_bytes is file size in bytes.
    """
    doc_id: str
    path: str
    is_active: bool
    mtime_iso: Optional[str] = None
    size_bytes: Optional[int] = None
    note: Optional[str] = None


@dataclass
class PersistDomainReport:
    """
    Domain integrity report: useful for diagnostics and repair workflows.

    Typical checks:
      - index.json exists and parses
      - active doc exists
      - doc ids are well-formed
      - next_id is consistent with existing docs
    """
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        """True if there are no errors."""
        return len(self.errors) == 0
