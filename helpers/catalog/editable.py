# helpers/catalog/editable.py
# Editable in-memory representation of a catalog: raw dict + optional undo/redo history + validation bridge.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, Optional, TypeVar, Union, cast

from helpers.history import History

from .catalog import Catalog

DocT = TypeVar("DocT")
ValidateFn = Callable[[Any], DocT]
DumpFn = Callable[[DocT], Dict[str, Any]]

RawCatalog = Dict[str, Any]
CatalogLike = Union[Catalog[DocT], DocT]


@dataclass
class EditableCatalog(Generic[DocT]):
    """
    In-memory editable view of a catalog.

    Rationale:
      - keep editing separate from validated immutable dataclasses/typed docs
      - allow partial edits without re-validating on every keystroke
      - validate only when committing (save/export)
      - optional History for undo/redo (caller chooses mutable vs immutable applier)
    """
    raw: RawCatalog
    schema_name: str = "catalog"
    schema_version: int = 1
    history: Optional[History] = None

    @staticmethod
    def from_catalog(
        catalog: CatalogLike[DocT],
        dump_fn: DumpFn[DocT],
        *,
        schema_name: str = "catalog",
        schema_version: int = 1,
        history: Optional[History] = None,
    ) -> "EditableCatalog[DocT]":
        """
        Create an editable view from either:
          - a Catalog[DocT], or
          - a typed doc (DocT)

        We intentionally accept both to keep call sites ergonomic.
        """
        doc = catalog.doc if isinstance(catalog, Catalog) else cast(DocT, catalog)
        raw = dump_fn(doc)
        return EditableCatalog(
            raw=raw,
            schema_name=schema_name,
            schema_version=schema_version,
            history=history,
        )

    def validate(self, validate_fn: ValidateFn[DocT]) -> DocT:
        """
        Validate the current raw state into a typed doc.
        """
        return validate_fn(self.raw)

    def to_catalog(self, *, validate: ValidateFn[DocT]) -> Catalog[DocT]:
        """
        Validate and convert this editable state into an immutable Catalog.
        """
        doc = validate(self.raw)
        return Catalog(doc=doc, schema_name=self.schema_name, schema_version=self.schema_version)
