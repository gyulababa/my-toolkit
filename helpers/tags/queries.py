# helpers/tags/queries.py
from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Tuple

from .types import Tag, TagCatalog, TagNamespace, TagSet
from .validators import parse_tag


def split_tags(tags: Sequence[str]) -> List[Tag]:
    return [parse_tag(t, path="tag") for t in tags]


def group_by_namespace(tags: Sequence[str]) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for s in tags:
        t = parse_tag(s, path="tag")
        out.setdefault(t.namespace, []).append(t.value)
    return out


def filter_by_namespace(tags: Sequence[str], namespace: str) -> List[str]:
    ns = namespace.strip().lower()
    prefix = f"{ns}:"
    return [t for t in tags if t.lower().startswith(prefix)]


def list_known_namespaces(catalog: TagCatalog, *, scope: str = "*") -> List[str]:
    return [ns.name for ns in catalog.namespaces_for_scope(scope)]


def suggest_values(catalog: TagCatalog, namespace: str) -> List[str]:
    ns = catalog.get_namespace(namespace.strip().lower())
    if not ns or not ns.allowed_values:
        return []
    return list(ns.allowed_values)
