# helpers/catalogloader/persistedloader.py
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Generic, Optional, TypeVar

from helpers.catalog import Catalog, EditableCatalog
from helpers.catalogloader.loader import CatalogLoader
from helpers.validation import ValidationError
from helpers.catalogloader.persisted_index import PersistIndex, load_index, save_index
from helpers.catalogloader.persisted_paths import domain_root, doc_path
from helpers.fs.dirs import ensure_dir

DocT = TypeVar("DocT")


def _format_id(n: int) -> str:
    return f"{n:04d}"


@dataclass
class PersistedCatalogLoader(Generic[DocT]):
    """
    PersistedCatalogLoader

    Bridges:
    - CatalogLoader (schema-pluggable typed validation/dump)
    - a persisted domain folder with index + numbered revision docs

    Domain layout:
      <persist_root>/<domain>/
        index.json
        0001.json
        0002.json
        ...

    The app decides persist_root. Helpers remain agnostic.
    """
    loader: CatalogLoader[DocT]
    domain: str
    seed_raw: Callable[[], Dict[str, Any]]  # used when domain not initialized

    def domain_dir(self, persist_root: Path) -> Path:
        return domain_root(persist_root, self.domain)

    def ensure_seeded(self, persist_root: Path, *, note: str = "seed") -> PersistIndex:
        """
        Ensure domain has index + at least one doc. If missing, create 0001 + index.json.
        """
        idx = load_index(persist_root, self.domain)
        if idx is not None:
            # verify active exists
            ap = doc_path(persist_root, self.domain, idx.active_id)
            if not ap.exists():
                raise ValidationError(f"Persist index points to missing doc: {ap}")
            return idx

        # seed new domain
        ensure_dir(self.domain_dir(persist_root))
        doc_id = _format_id(1)
        doc_file = doc_path(persist_root, self.domain, doc_id)

        raw = self.seed_raw()
        if not isinstance(raw, dict):
            raise ValidationError(f"seed_raw() must return dict for domain '{self.domain}'")

        # validate (fail early)
        _ = self.loader.validate(raw)

        self.loader.save_raw(doc_file, raw, indent=2)

        idx = PersistIndex(active_id=doc_id, next_int=2, history=[{"op": "seed", "doc_id": doc_id, "note": note}])
        save_index(persist_root, self.domain, idx)
        return idx

    def active_path(self, persist_root: Path) -> Path:
        idx = self.ensure_seeded(persist_root)
        return doc_path(persist_root, self.domain, idx.active_id)

    def list_doc_ids(self, persist_root: Path) -> list[str]:
        d = self.domain_dir(persist_root)
        if not d.exists():
            return []
        out: list[str] = []
        for p in sorted(d.glob("*.json")):
            if p.name == "index.json":
                continue
            out.append(p.stem)
        return out

    # -------------------------
    # Load specific revision (preview-only; does NOT promote)
    # -------------------------
    def load_revision_raw(self, persist_root: Path, doc_id: str) -> Dict[str, Any]:
        """Load a specific persisted revision as raw JSON (dict)."""
        _ = self.ensure_seeded(persist_root)
        p = doc_path(persist_root, self.domain, doc_id)
        if not p.exists():
            raise ValidationError(f"Cannot load missing doc '{doc_id}' for domain '{self.domain}'")
        return self.loader.load_raw(p)

    def load_revision_catalog(self, persist_root: Path, doc_id: str) -> Catalog[DocT]:
        """Load+validate a specific persisted revision and return an immutable Catalog wrapper."""
        raw = self.load_revision_raw(persist_root, doc_id)
        return Catalog.load(raw, validate=self.loader.validate, schema_name=self.loader.schema_name, schema_version=self.loader.schema_version)

    def load_revision_editable(self, persist_root: Path, doc_id: str, *, history=None) -> EditableCatalog[DocT]:
        """Load a specific persisted revision into an EditableCatalog (no promotion)."""
        raw = self.load_revision_raw(persist_root, doc_id)
        return EditableCatalog(raw=raw, schema_name=self.loader.schema_name, schema_version=self.loader.schema_version, history=history)

    def load_active_catalog(self, persist_root: Path) -> Catalog[DocT]:
        p = self.active_path(persist_root)
        raw = self.loader.load_raw(p)
        return Catalog.load(raw, validate=self.loader.validate, schema_name=self.loader.schema_name, schema_version=self.loader.schema_version)

    def load_active_editable(self, persist_root: Path, *, history=None) -> EditableCatalog[DocT]:
        p = self.active_path(persist_root)
        raw = self.loader.load_raw(p)
        return EditableCatalog(raw=raw, schema_name=self.loader.schema_name, schema_version=self.loader.schema_version, history=history)

    def promote_existing(self, persist_root: Path, doc_id: str, *, note: str = "promote") -> None:
        idx = self.ensure_seeded(persist_root)
        p = doc_path(persist_root, self.domain, doc_id)
        if not p.exists():
            raise ValidationError(f"Cannot promote missing doc '{doc_id}' for domain '{self.domain}'")

        hist = list(idx.history) if idx.history is not None else []
        hist.append({"op": "promote", "doc_id": doc_id, "note": note})

        new_idx = PersistIndex(active_id=doc_id, next_int=idx.next_int, history=hist)
        save_index(persist_root, self.domain, new_idx)

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
        Save editable raw as a new numbered revision doc.

        Returns path to the new doc file.
        """
        idx = self.ensure_seeded(persist_root)

        if validate_before_save:
            _ = self.loader.validate(editable.raw)

        doc_id = _format_id(idx.next_int)
        p = doc_path(persist_root, self.domain, doc_id)

        self.loader.save_raw(p, editable.raw, indent=2)

        hist = list(idx.history) if idx.history is not None else []
        hist.append({"op": "save", "doc_id": doc_id, "note": note})

        new_active = doc_id if make_active else idx.active_id
        new_idx = PersistIndex(active_id=new_active, next_int=idx.next_int + 1, history=hist)
        save_index(persist_root, self.domain, new_idx)

        return p
