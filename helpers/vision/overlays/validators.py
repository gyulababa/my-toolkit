# helpers/vision/overlays/validators.py

from __future__ import annotations

from typing import Any, Dict

from helpers.validation import ValidationError


def validate_layer_catalog(raw: Any) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValidationError("layer_catalog: root must be an object")

    schema = raw.get("schema")
    if schema != "vision.layer_catalog.v1":
        raise ValidationError(f"layer_catalog: unsupported schema={schema!r}")

    _require_dict(raw, "meta")
    _require_dict(raw, "viewport")
    _require_dict(raw, "style_presets")
    _require_list(raw, "layers")

    ids = set()
    for i, layer in enumerate(raw["layers"]):
        if not isinstance(layer, dict):
            raise ValidationError(f"layer_catalog.layers[{i}]: expected object")
        _require_str(layer, "id")
        _require_str(layer, "name")
        _require_str(layer, "kind")
        _require_int(layer, "z")
        lid = layer["id"]
        if lid in ids:
            raise ValidationError(f"layer_catalog: duplicate layer id {lid!r}")
        ids.add(lid)

    return raw


def validate_annotation_catalog(raw: Any) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValidationError("annotation_catalog: root must be an object")

    schema = raw.get("schema")
    if schema != "vision.annotation_catalog.v1":
        raise ValidationError(f"annotation_catalog: unsupported schema={schema!r}")

    _require_dict(raw, "meta")
    _require_list(raw, "sets")

    set_ids = set()
    for i, s in enumerate(raw["sets"]):
        if not isinstance(s, dict):
            raise ValidationError(f"annotation_catalog.sets[{i}]: expected object")
        _require_str(s, "id")
        _require_str(s, "name")
        _require_list(s, "annotations")

        sid = s["id"]
        if sid in set_ids:
            raise ValidationError(f"annotation_catalog: duplicate set id {sid!r}")
        set_ids.add(sid)

        ann_ids = set()
        for j, a in enumerate(s["annotations"]):
            if not isinstance(a, dict):
                raise ValidationError(f"annotation_catalog.sets[{i}].annotations[{j}]: expected object")
            _require_str(a, "id")
            _require_str(a, "kind")
            aid = a["id"]
            if aid in ann_ids:
                raise ValidationError(f"annotation_catalog.sets[{i}] ({sid!r}): duplicate annotation id {aid!r}")
            ann_ids.add(aid)

    return raw


def dump_identity(doc: Dict[str, Any]) -> Dict[str, Any]:
    # We keep DocT=dict for now; later you can dump dataclasses here.
    return doc


def _require_str(d: Dict[str, Any], k: str) -> None:
    v = d.get(k)
    if not isinstance(v, str) or not v:
        raise ValidationError(f"missing/invalid string field: {k!r}")


def _require_int(d: Dict[str, Any], k: str) -> None:
    v = d.get(k)
    if not isinstance(v, int):
        raise ValidationError(f"missing/invalid int field: {k!r}")


def _require_dict(d: Dict[str, Any], k: str) -> None:
    v = d.get(k)
    if not isinstance(v, dict):
        raise ValidationError(f"missing/invalid object field: {k!r}")


def _require_list(d: Dict[str, Any], k: str) -> None:
    v = d.get(k)
    if not isinstance(v, list):
        raise ValidationError(f"missing/invalid array field: {k!r}")
