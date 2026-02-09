# helpers/tags/types.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Set, Tuple


@dataclass(frozen=True)
class Tag:
    """
    Parsed tag in canonical form.

    Canonical string form:
      "<namespace>:<value>"
    """
    namespace: str
    value: str

    def to_str(self) -> str:
        return f"{self.namespace}:{self.value}"


@dataclass(frozen=True)
class TagNamespace:
    """
    Namespace definition (registry entry).
    """
    name: str
    description: Optional[str] = None
    multi_valued: bool = True
    allowed_values: Optional[Tuple[str, ...]] = None
    applies_to: Optional[Tuple[str, ...]] = None  # scope hints; app-defined strings


@dataclass(frozen=True)
class TagCatalog:
    """
    Registry of namespaces + constraints.

    Stored as:
      namespaces_by_name[name] -> TagNamespace
    """
    namespaces_by_name: Dict[str, TagNamespace]
    schema_name: str = "tag_catalog"
    schema_version: int = 1

    def get_namespace(self, name: str) -> Optional[TagNamespace]:
        return self.namespaces_by_name.get(name)

    def namespaces_for_scope(self, scope: str) -> List[TagNamespace]:
        out: List[TagNamespace] = []
        for ns in self.namespaces_by_name.values():
            if not ns.applies_to or "*" in ns.applies_to or scope in ns.applies_to:
                out.append(ns)
        return sorted(out, key=lambda x: x.name)


@dataclass
class TagSet:
    """
    Convenience wrapper around a list of tag strings (canonical "<ns>:<value>").

    - keeps insertion order
    - ensures uniqueness
    - supports single-valued namespace enforcement (via catalog)
    """
    items: List[str]

    def __post_init__(self) -> None:
        # preserve order while removing duplicates
        seen: Set[str] = set()
        out: List[str] = []
        for t in self.items:
            if t not in seen:
                out.append(t)
                seen.add(t)
        self.items = out

    def to_list(self) -> List[str]:
        return list(self.items)

    def has(self, tag_str: str) -> bool:
        return tag_str in self.items

    def add(self, tag_str: str) -> None:
        if tag_str not in self.items:
            self.items.append(tag_str)

    def remove(self, tag_str: str) -> None:
        try:
            self.items.remove(tag_str)
        except ValueError:
            pass

    def clear_namespace(self, namespace: str) -> None:
        prefix = f"{namespace}:"
        self.items = [t for t in self.items if not t.startswith(prefix)]

    def get_values(self, namespace: str) -> List[str]:
        prefix = f"{namespace}:"
        out: List[str] = []
        for t in self.items:
            if t.startswith(prefix):
                out.append(t[len(prefix):])
        return out
