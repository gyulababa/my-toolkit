# helpers/catalog/catalog.py
# Core typed container for a validated catalog document (schema-tagged, immutable, IO-free).

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, TypeVar

DocT = TypeVar("DocT")

ValidateFn = Callable[[Any], DocT]
DumpFn = Callable[[DocT], Dict[str, Any]]


@dataclass(frozen=True)
class Catalog(Generic[DocT]):
    """
    Validated, immutable-ish catalog container.

    Design intent:
      - `doc` is a validated typed object (dict, dataclass graph, etc.)
      - IO is deliberately out of scope (handled by catalogloader + fs helpers)
      - schema_name/version are stored for provenance/debugging and forward compatibility
    """
    doc: DocT
    schema_name: str = "catalog"
    schema_version: int = 1

    @staticmethod
    def load(
        raw: Any,
        *,
        validate: ValidateFn[DocT],
        schema_name: str = "catalog",
        schema_version: int = 1,
    ) -> "Catalog[DocT]":
        """
        Validate a raw document and return a Catalog.

        The validate function is expected to raise helpers.validation.ValidationError
        (or compatible exceptions) on failures.
        """
        doc = validate(raw)
        return Catalog(doc=doc, schema_name=schema_name, schema_version=schema_version)

    def dump(self, dump_fn: DumpFn[DocT]) -> Dict[str, Any]:
        """
        Convert the typed doc back into a JSON-serializable dict.
        """
        return dump_fn(self.doc)

    def schema_tag(self) -> str:
        """
        Return a stable schema tag string for logs/debugging.
        Example: "catalog@1"
        """
        return f"{self.schema_name}@{self.schema_version}"
