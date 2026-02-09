# helpers/catalogloader/persistedloader.py
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Generic, Optional, TypeVar

from helpers.catalog import Catalog, EditableCatalog
from helpers.catalogloader.loader import CatalogLoader
from helpers.validation import ValidationError
from helpers.fs_utils import ensure_dir, atomic_write_text  # later: helpers.fs.*

DocT = TypeVar("DocT")


@dataclass(frozen=True)
class PersistIndex:
    """
    Domain index stored at:
      <persist_root>/<domain>/index.json

    Minimal schema (v1):
      {
        "schema_name": "persist_index",
        "schema_version": 1,
        "active_id": "0001",
        "next_int": 2,
        "history": [{"op":"seed","doc_id":"0001","note": "...", "ts": "..."}] (optional)
      }
    """
    active_id: str
    next_int: int
    schema_name: str = "persist_index"
    schema_version: int = 1
    history: Optional[list[dict]] = None


def _format_id(n: int) -> str:
    return f"{n:04d}"


def _index_path(persist_root: Path, domain: str) -> Path:
    return Path(persist_root) / domain / "index.json"


def _doc_path(persist_root: Path, domain: str, doc_id: str) -> Path:
    return Path(persist_root) / domain / f"{doc_id}.json"


def _read_index(persist_root: Path, domain: str) -> Optional[PersistIndex]:
    p = _index_path(persist_root, domain)
    if not p.exists():
        return None
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise ValidationError(f"Failed to read persist index: {p}") from e

    if not isinstance(raw, dict):
        raise ValidationError(f"Persist index must be an object: {p}")

    active_id = raw.get("active_id")
    next_int = raw.get("next_int")

    if not isinstance(active_id, str) or not active_id:
        raise ValidationError(f"Persist index missing/invalid 'active_id': {p}")
    if not isinstance(next_int, int) or next_int < 1:
        raise ValidationError(f"Persist index missing/invalid 'next_int': {p}")

    hist = raw.get("history")
    if hist is not None and not isinstance(hist, list):
        raise ValidationError(f"Persist index 'history' must be a list: {p}")

    return PersistIndex(active_id=active_id, next_int=next_int, history=hist)


def _write_index(persist_root: Path, domain: str, idx: PersistIndex) -> None:
    p = _index_path(persist_root, domain)
    ensure_dir(p.parent)
    raw: Dict[str, Any] = {
        "schema_name": idx.schema_name,
        "schema_version": idx.schema_version,
        "active_id": idx.active_id,
        "next_int": idx.next_int,
    }
    if idx.history is not None:
        raw["history"] = idx.history
    text = json.dumps(raw, indent=2, ensure_ascii=False, sort_keys=True)
    atomic_write_text(p, text, encoding="utf-8")


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
        return Path(persist_root) / self.domain

    def ensure_seeded(self, persist_root: Path, *, note: str = "seed") -> PersistIndex:
        """
        Ensure domain has index + at least one doc. If missing, create 0001 + index.json.
        """
        idx = _read_index(persist_root, self.domain)
        if idx is not None:
            # verify active exists
            ap = _doc_path(persist_root, self.domain, idx.active_id)
            if not ap.exists():
                raise ValidationError(f"Persist index points to missing doc: {ap}")
            return idx

        # seed new domain
        ensure_dir(self.domain_dir(persist_root))
        doc_id = _format_id(1)
        doc_path = _doc_path(persist_root, self.domain, doc_id)

        raw = self.seed_raw()
        if not isinstance(raw, dict):
            raise ValidationError(f"seed_raw() must return dict for domain '{self.domain}'")

        # validate (fail early)
        _ = self.loader.validate(raw)

        self.loader.save_raw(doc_path, raw, indent=2)

        idx = PersistIndex(active_id=doc_id, next_int=2, history=[{"op": "seed", "doc_id": doc_id, "note": note}])
        _write_index(persist_root, self.domain, idx)
        return idx

    def active_path(self, persist_root: Path) -> Path:
        idx = self.ensure_seeded(persist_root)
        return _doc_path(persist_root, self.domain, idx.active_id)

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
        p = _doc_path(persist_root, self.domain, doc_id)
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
        p = _doc_path(persist_root, self.domain, doc_id)
        if not p.exists():
            raise ValidationError(f"Cannot promote missing doc '{doc_id}' for domain '{self.domain}'")

        hist = list(idx.history) if idx.history is not None else []
        hist.append({"op": "promote", "doc_id": doc_id, "note": note})

        new_idx = PersistIndex(active_id=doc_id, next_int=idx.next_int, history=hist)
        _write_index(persist_root, self.domain, new_idx)

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
        p = _doc_path(persist_root, self.domain, doc_id)

        self.loader.save_raw(p, editable.raw, indent=2)

        hist = list(idx.history) if idx.history is not None else []
        hist.append({"op": "save", "doc_id": doc_id, "note": note})

        new_active = doc_id if make_active else idx.active_id
        new_idx = PersistIndex(active_id=new_active, next_int=idx.next_int + 1, history=hist)
        _write_index(persist_root, self.domain, new_idx)

        return p
