# helpers/persist/persisted_catalog_loader.py
# PersistedCatalogLoader: persist-domain adapter around CatalogLoader that standardizes index/doc naming and revisions.

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Generic, Optional, TypeVar

from helpers.catalog import Catalog, EditableCatalog
from helpers.catalogloader.loader import CatalogLoader
from helpers.validation import ValidationError

from .index import (
    ensure_seeded,
    read_index,
    allocate_next_id,
    set_active,
)
from .paths import doc_path

DocT = TypeVar("DocT")
SeedFn = Callable[[], Dict[str, Any]]


@dataclass
class PersistedCatalogLoader(Generic[DocT]):
    """
    PersistedCatalogLoader

    A small adapter that standardizes:
      <persist_root>/<domain>/index.json
      <persist_root>/<domain>/0001.json, 0002.json...

    Uses CatalogLoader for JSON IO + schema validation/dump consistency.
    """
    loader: CatalogLoader[DocT]
    domain: str
    seed_raw: Optional[SeedFn] = None
    indent: int = 2

    def _ensure_seeded(self, persist_root: Path) -> None:
        """Ensure the domain has index.json and an initial 0001.json doc."""
        ensure_seeded(
            persist_root,
            self.domain,
            seed_doc_id="0001",
            seed_raw=self.seed_raw() if self.seed_raw else {},
            indent=self.indent,
        )

    def active_id(self, persist_root: Path) -> str:
        """Return the active doc id from index.json."""
        self._ensure_seeded(persist_root)
        idx = read_index(persist_root, self.domain)
        return idx.active_id

    def active_path(self, persist_root: Path) -> Path:
        """Return the active doc path (<domain>/<active_id>.json)."""
        return doc_path(persist_root, self.domain, self.active_id(persist_root))

    # -------------------------
    # Load specific revision (preview-only; does NOT promote)
    # -------------------------
    def load_revision_raw(self, persist_root: Path, doc_id: str) -> Dict[str, Any]:
        """Load a specific persisted revision as raw JSON (dict)."""
        self._ensure_seeded(persist_root)
        p = doc_path(persist_root, self.domain, doc_id)
        if not p.exists():
            raise ValidationError(f"Missing persisted doc: {p}")
        return self.loader.load_raw(p)

    def load_revision_editable(
        self,
        persist_root: Path,
        doc_id: str,
        *,
        history=None,
    ) -> EditableCatalog[DocT]:
        """Load a specific persisted revision into an EditableCatalog (no promotion)."""
        raw = self.load_revision_raw(persist_root, doc_id)
        return EditableCatalog(
            raw=raw,
            schema_name=self.loader.schema_name,
            schema_version=self.loader.schema_version,
            history=history,
        )

    def load_revision_catalog(self, persist_root: Path, doc_id: str) -> Catalog[DocT]:
        """Load+validate a specific persisted revision and return an immutable Catalog wrapper."""
        raw = self.load_revision_raw(persist_root, doc_id)
        return Catalog.load(
            raw,
            validate=self.loader.validate,
            schema_name=self.loader.schema_name,
            schema_version=self.loader.schema_version,
        )

    # -------------------------
    # Load active
    # -------------------------
    def load_active_raw(self, persist_root: Path) -> Dict[str, Any]:
        """Load the active doc as raw JSON (dict)."""
        self._ensure_seeded(persist_root)
        return self.loader.load_raw(self.active_path(persist_root))

    def load_active_catalog(self, persist_root: Path) -> Catalog[DocT]:
        """Load+validate the active doc and return an immutable Catalog wrapper."""
        raw = self.load_active_raw(persist_root)
        return Catalog.load(
            raw,
            validate=self.loader.validate,
            schema_name=self.loader.schema_name,
            schema_version=self.loader.schema_version,
        )

    def load_active_editable(self, persist_root: Path, *, history=None) -> EditableCatalog[DocT]:
        """Load the active doc into an EditableCatalog (caller may attach history/undo)."""
        raw = self.load_active_raw(persist_root)
        return EditableCatalog(
            raw=raw,
            schema_name=self.loader.schema_name,
            schema_version=self.loader.schema_version,
            history=history,
        )

    # -------------------------
    # Save new revision (standardized)
    # -------------------------
    def save_new_revision(
        self,
        persist_root: Path,
        editable: EditableCatalog[DocT],
        *,
        note: Optional[str] = None,
        validate_before_save: bool = True,
        make_active: bool = True,
    ) -> Path:
        """
        Write a new numbered doc (000N.json). Optionally set it as active.

        Returns:
          Path to the written file.
        """
        self._ensure_seeded(persist_root)

        # Optional pre-save validation step.
        if validate_before_save:
            _ = editable.validate(self.loader.validate)

        new_id = allocate_next_id(persist_root, self.domain, note=note)
        p = doc_path(persist_root, self.domain, new_id)

        # Use CatalogLoader's JSON writer for consistency of dumps/formatting.
        self.loader.save_raw(p, editable.raw, indent=self.indent)

        if make_active:
            set_active(persist_root, self.domain, new_id, note=f"set active{': ' + note if note else ''}")

        return p

    def promote_existing(self, persist_root: Path, doc_id: str, *, note: Optional[str] = None) -> None:
        """
        Set an existing doc as active (no write).

        Raises:
          ValidationError if the doc file does not exist.
        """
        self._ensure_seeded(persist_root)
        p = doc_path(persist_root, self.domain, doc_id)
        if not p.exists():
            raise ValidationError(f"Cannot set active: missing persisted doc: {p}")
        set_active(persist_root, self.domain, doc_id, note=note)

    def validate_doc(self, persist_root: Path, doc_id: str) -> Catalog[DocT]:
        """
        Validate a specific persisted doc by id and return a Catalog.

        Raises:
          ValidationError (via CatalogLoader/Catalog) if schema validation fails.
        """
        self._ensure_seeded(persist_root)
        p = doc_path(persist_root, self.domain, doc_id)
        raw = self.loader.load_raw(p)
        return Catalog.load(
            raw,
            validate=self.loader.validate,
            schema_name=self.loader.schema_name,
            schema_version=self.loader.schema_version,
        )
