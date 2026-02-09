# helpers/zones/schema.py
from __future__ import annotations

"""helpers.zones.schema

Lightweight validation for the zones preset library document.

Goals:
- Stable, human-readable error paths (ValidationError)
- Validate structure and basic types
- Avoid overfitting: consumer payloads are treated as opaque dicts

This module intentionally does NOT validate:
- specific consumer schemas ("ocr", "search", etc.)
- domain rules about intent values beyond "string"
"""

from typing import Any, Dict

from helpers.validation.basic import (
    ValidationError,
    ensure_bool,
    ensure_dict,
    ensure_list,
    ensure_one_of,
    ensure_str,
)

_GEOM_TYPES = ("rect_px", "rect_norm")


def ensure_geometry_shape(geom: Any, *, path: str = "geometry") -> Dict[str, Any]:
    g = ensure_dict(geom, path=path)

    gtype = ensure_str(g.get("type"), path=f"{path}.type")
    ensure_one_of(gtype, _GEOM_TYPES, path=f"{path}.type")

    arr = ensure_list(g.get("xyxy"), path=f"{path}.xyxy")
    if len(arr) != 4:
        raise ValidationError(f"{path}.xyxy must have 4 numbers (got {len(arr)})")
    for i, v in enumerate(arr):
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise ValidationError(f"{path}.xyxy[{i}] must be a number (got {type(v).__name__})")

    return g


def ensure_zone_shape(zone: Any, *, path: str = "zone") -> Dict[str, Any]:
    z = ensure_dict(zone, path=path)

    if "enabled" in z:
        ensure_bool(z["enabled"], path=f"{path}.enabled")

    if "intent" in z:
        ensure_str(z["intent"], path=f"{path}.intent")

    if "geometry" in z:
        ensure_geometry_shape(z["geometry"], path=f"{path}.geometry")

    if "tags" in z:
        tags = ensure_list(z["tags"], path=f"{path}.tags")
        for i, t in enumerate(tags):
            ensure_str(t, path=f"{path}.tags[{i}]", allow_empty=True)

    if "style" in z:
        ensure_dict(z["style"], path=f"{path}.style")

    if "consumers" in z:
        consumers = ensure_dict(z["consumers"], path=f"{path}.consumers")
        for ck, payload in consumers.items():
            ensure_str(ck, path=f"{path}.consumers.<key>")
            ensure_dict(payload, path=f"{path}.consumers.{ck}")

    return z


def ensure_library_shape(doc: Any, *, path: str = "$") -> Dict[str, Any]:
    d = ensure_dict(doc, path=path)

    sv = d.get("schema_version")
    if sv != 1:
        raise ValidationError(f"{path}.schema_version must be 1 (got {sv!r})")

    presets = ensure_dict(d.get("presets"), path=f"{path}.presets")

    for preset_id, preset in presets.items():
        ensure_str(preset_id, path=f"{path}.presets.<preset_id>")
        p = ensure_dict(preset, path=f"{path}.presets.{preset_id}")

        if "meta" in p:
            meta = ensure_dict(p["meta"], path=f"{path}.presets.{preset_id}.meta")
            if "name" in meta:
                ensure_str(meta["name"], path=f"{path}.presets.{preset_id}.meta.name")
            if "tags" in meta:
                mtags = ensure_list(meta["tags"], path=f"{path}.presets.{preset_id}.meta.tags")
                for i, t in enumerate(mtags):
                    ensure_str(t, path=f"{path}.presets.{preset_id}.meta.tags[{i}]", allow_empty=True)

        zones = ensure_dict(p.get("zones"), path=f"{path}.presets.{preset_id}.zones")
        for zone_key, zone in zones.items():
            ensure_str(zone_key, path=f"{path}.presets.{preset_id}.zones.<zone_key>")
            ensure_zone_shape(zone, path=f"{path}.presets.{preset_id}.zones.{zone_key}")

    return d
