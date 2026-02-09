# services/domain/base_domain_service.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Generic, Optional, TypeVar

from helpers.catalog import EditableCatalog, Catalog
from helpers.persist import PersistedCatalogLoader
from helpers.persist.index import list_doc_ids, read_index
from helpers.validation import ValidationError
from helpers.history import History

DocT = TypeVar("DocT")


@dataclass
class BaseDomainService(Generic[DocT]):
    persist_root: Path
    persisted: PersistedCatalogLoader[DocT]

    # Mutable runtime state:
    history: History = History()
    current: Optional[EditableCatalog[DocT]] = None

    @property
    def domain(self) -> str:
        return self.persisted.domain

    def load_active(self) -> EditableCatalog[DocT]:
        self.history.clear()  # or reset; depends on your History API
        self.current = self.persisted.load_active_editable(self.persist_root, history=self.history)
        return self.current

    def list_revisions(self) -> list[dict]:
        idx = read_index(self.persist_root, self.domain)
        ids = list_doc_ids(self.persist_root, self.domain)
        return [{"doc_id": i, "is_active": (i == idx.active_id)} for i in ids]

    def load_revision(self, doc_id: str, *, promote: bool = False) -> EditableCatalog[DocT]:
        if promote:
            self.persisted.promote_existing(self.persist_root, doc_id, note="promote via UI")
            return self.load_active()

        # Without a helper addition, "preview without promote" is:
        # - load doc path directly via underlying loader
        p = self.persisted.loader  # CatalogLoader
        raw = p.load_raw(self.persisted.active_path(self.persist_root).parent / f"{doc_id}.json")
        self.history.clear()
        self.current = EditableCatalog(
            raw=raw,
            schema_name=p.schema_name,
            schema_version=p.schema_version,
            history=self.history,
        )
        return self.current

    def validate_current(self) -> Catalog[DocT]:
        if self.current is None:
            raise ValidationError(f"{self.domain}: nothing loaded")
        return self.current.validate(self.persisted.loader.validate)

    def save_new(self, *, note: Optional[str] = None) -> str:
        if self.current is None:
            raise ValidationError(f"{self.domain}: nothing loaded")
        out_path = self.persisted.save_new_revision(
            self.persist_root,
            self.current,
            note=note,
            validate_before_save=True,
            make_active=True,
        )
        # Reload to ensure clean state and history reset
        self.load_active()
        return out_path.stem  # "0007"

    # Undo/redo delegates to History (implementation-specific)
    def can_undo(self) -> bool:
        return self.history.can_undo()

    def can_redo(self) -> bool:
        return self.history.can_redo()

    def undo(self) -> None:
        self.history.undo(self.current.raw)  # or however your History applies

    def redo(self) -> None:
        self.history.redo(self.current.raw)
