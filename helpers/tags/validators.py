# helpers/tags/validators.py

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

from helpers.validation import ValidationError
from helpers.validation.basic import require_dict, require_list_of_dicts, require_str, require_bool  # compat
from helpers.validation.basic import require_one_of  # if you have it; ok if unused

from .types import Tag, TagCatalog, TagNamespace, TagSet


_NS_RE = re.compile(r"^[a-z][a-z0-9_]*(?:[.-][a-z0-9_]+)*$", re.IGNORECASE)
# value: allow fairly broad, but forbid whitespace at ends; forbid empty
# (if you want stricter: swap regex)
_VAL_RE = re.compile(r"^[^\s].*[^\s]$")


def parse_tag(tag: str, *, path: str = "tag") -> Tag:
    """
    Parse "ns:value" into Tag.

    Rules:
    - exactly one ":" separator (first colon splits)
    - namespace matches _NS_RE
    - value non-empty and trimmed
    """
    if not isinstance(tag, str):
        raise ValidationError(f"{path} must be a string (got {type(tag).__name__})")

    raw = tag.strip()
    if not raw:
        raise ValidationError(f"{path} must be non-empty")

    if ":" not in raw:
        raise ValidationError(f"{path} must be in 'namespace:value' form (got {tag!r})")

    ns, val = raw.split(":", 1)
    ns = ns.strip()
    val = val.strip()

    if not ns or not val:
        raise ValidationError(f"{path} must be in 'namespace:value' form (got {tag!r})")

    if not _NS_RE.match(ns):
        raise ValidationError(f"{path} has invalid namespace {ns!r}")

    if not _VAL_RE.match(val):
        raise ValidationError(f"{path} has invalid value {val!r}")

    return Tag(namespace=ns, value=val)


def normalize_tag_str(tag: str, *, lower_namespace: bool = True) -> str:
    """
    Normalize a tag string:
    - trim whitespace
    - optionally lower-case namespace
    - keep value as-is (except trimming)
    """
    t = parse_tag(tag, path="tag")
    ns = t.namespace.lower() if lower_namespace else t.namespace
    return f"{ns}:{t.value}"


def validate_tag_str(tag: str, catalog: Optional[TagCatalog] = None, *, scope: str = "*", path: str = "tag") -> str:
    """
    Validate a tag string, optionally against TagCatalog constraints.
    Returns canonical normalized tag string (namespace lower-cased).
    """
    s = normalize_tag_str(tag, lower_namespace=True)
    t = parse_tag(s, path=path)

    if catalog is None:
        return s

    ns = catalog.get_namespace(t.namespace)
    if ns is None:
        raise ValidationError(f"{path}: unknown namespace '{t.namespace}'")

    # scope filtering is advisory; enforcement optional
    if ns.applies_to and "*" not in ns.applies_to and scope not in ns.applies_to:
        raise ValidationError(f"{path}: namespace '{t.namespace}' not allowed for scope '{scope}'")

    if ns.allowed_values is not None:
        if t.value not in ns.allowed_values:
            raise ValidationError(
                f"{path}: value '{t.value}' not allowed for namespace '{t.namespace}'"
            )

    return s


def validate_tagset(
    tags: Sequence[str],
    catalog: Optional[TagCatalog] = None,
    *,
    scope: str = "*",
    path: str = "tags",
) -> TagSet:
    """
    Validate/normalize a list of tags.

    If catalog provided, enforces:
    - namespace existence
    - allowed_values
    - scope applies_to (strict)
    - single-valued namespaces (multi_valued=False)
    """
    if not isinstance(tags, (list, tuple)):
        raise ValidationError(f"{path} must be a list (got {type(tags).__name__})")

    out: List[str] = []
    # normalize+basic validate
    for i, raw in enumerate(tags):
        out.append(validate_tag_str(str(raw), catalog=catalog, scope=scope, path=f"{path}[{i}]"))

    tagset = TagSet(out)

    # enforce multi_valued constraints
    if catalog is not None:
        counts: Dict[str, int] = {}
        for s in tagset.items:
            t = parse_tag(s, path=path)
            counts[t.namespace] = counts.get(t.namespace, 0) + 1

        for ns_name, count in counts.items():
            ns = catalog.get_namespace(ns_name)
            if ns and not ns.multi_valued and count > 1:
                raise ValidationError(f"{path}: namespace '{ns_name}' is single-valued; got {count} values")

    return tagset


def apply_tag_add(
    tagset: TagSet,
    tag: str,
    catalog: Optional[TagCatalog] = None,
    *,
    scope: str = "*",
) -> TagSet:
    """
    Add a tag to a set, respecting catalog constraints.
    If the namespace is single-valued, replaces existing values in that namespace.
    """
    s = validate_tag_str(tag, catalog=catalog, scope=scope, path="tag")
    t = parse_tag(s, path="tag")

    if catalog is not None:
        ns = catalog.get_namespace(t.namespace)
        if ns and not ns.multi_valued:
            tagset.clear_namespace(t.namespace)

    tagset.add(s)
    return tagset


def apply_tag_remove(tagset: TagSet, tag: str) -> TagSet:
    """
    Remove a tag (normalized).
    """
    s = normalize_tag_str(tag, lower_namespace=True)
    tagset.remove(s)
    return tagset


# ─────────────────────────────────────────────────────────────
# Catalog schema validation
# ─────────────────────────────────────────────────────────────

def validate_tag_catalog(raw: Any) -> TagCatalog:
    """
    Validate a tag catalog document from raw JSON dict.

    Expected shape:
      {
        "schema_name": "tag_catalog" (optional),
        "schema_version": 1 (optional),
        "namespaces": [
          {
            "name": "topic",
            "description": "...",
            "multi_valued": true,
            "allowed_values": ["a","b"] (optional),
            "applies_to": ["*", "phrases"] (optional)
          }, ...
        ]
      }
    """
    doc = require_dict(raw, path="tag_catalog")
    ns_list = require_list_of_dicts(doc, "namespaces", path="tag_catalog", default=[])

    namespaces_by_name: Dict[str, TagNamespace] = {}

    for i, ns_raw in enumerate(ns_list):
        p = f"tag_catalog.namespaces[{i}]"
        name = require_str(ns_raw, "name", path=p)
        if not _NS_RE.match(name):
            raise ValidationError(f"{p}.name has invalid namespace name {name!r}")

        desc = ns_raw.get("description")
        if desc is not None and not isinstance(desc, str):
            raise ValidationError(f"{p}.description must be a string (got {type(desc).__name__})")

        multi = bool(ns_raw.get("multi_valued", True))
        if "multi_valued" in ns_raw and not isinstance(ns_raw["multi_valued"], bool):
            raise ValidationError(f"{p}.multi_valued must be a bool")

        allowed_values = ns_raw.get("allowed_values")
        allowed_t: Optional[Tuple[str, ...]] = None
        if allowed_values is not None:
            if not isinstance(allowed_values, list) or not all(isinstance(x, str) for x in allowed_values):
                raise ValidationError(f"{p}.allowed_values must be a list of strings")
            allowed_t = tuple(x.strip() for x in allowed_values if x.strip())

        applies_to = ns_raw.get("applies_to")
        applies_t: Optional[Tuple[str, ...]] = None
        if applies_to is not None:
            if not isinstance(applies_to, list) or not all(isinstance(x, str) for x in applies_to):
                raise ValidationError(f"{p}.applies_to must be a list of strings")
            applies_t = tuple(x.strip() for x in applies_to if x.strip())

        key = name.lower()
        if key in namespaces_by_name:
            raise ValidationError(f"{p}.name duplicate namespace '{name}'")

        namespaces_by_name[key] = TagNamespace(
            name=key,
            description=desc.strip() if isinstance(desc, str) else None,
            multi_valued=multi,
            allowed_values=allowed_t,
            applies_to=applies_t,
        )

    return TagCatalog(namespaces_by_name=namespaces_by_name, schema_name="tag_catalog", schema_version=1)
