from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class DocKey:
    kind: str          # e.g. "kb", "ticket", "route"
    doc_id: str        # stable ID in that kind


@dataclass(frozen=True)
class Doc:
    kind: str
    doc_id: str
    title: str
    body: str
    tags: str
    meta_json: str
    assignment_group: str
    deleted: int
    created_at: str
    updated_at: str
    rev: int


@dataclass(frozen=True)
class DocRevision:
    rev: int
    payload_json: str
    created_at: str
    note: str


@dataclass(frozen=True)
class SearchHit:
    kind: str
    doc_id: str
    title: str
    snippet: str
    score: Optional[float] = None
