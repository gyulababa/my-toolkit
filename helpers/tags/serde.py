# helpers/tags/serde.py

from __future__ import annotations

from typing import Any, Dict, List

from .types import TagCatalog, TagNamespace


def dump_tag_catalog(doc: TagCatalog) -> Dict[str, Any]:
    """
    Dump TagCatalog to a JSON-serializable dict.
    """
    namespaces: List[Dict[str, Any]] = []
    for ns in sorted(doc.namespaces_by_name.values(), key=lambda x: x.name):
        namespaces.append(
            {
                "name": ns.name,
                "description": ns.description,
                "multi_valued": ns.multi_valued,
                "allowed_values": list(ns.allowed_values) if ns.allowed_values is not None else None,
                "applies_to": list(ns.applies_to) if ns.applies_to is not None else None,
            }
        )

    # drop None fields for cleanliness
    for item in namespaces:
        for k in list(item.keys()):
            if item[k] is None:
                item.pop(k, None)

    return {
        "schema_name": doc.schema_name,
        "schema_version": doc.schema_version,
        "namespaces": namespaces,
    }
