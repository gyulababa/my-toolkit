# helpers/lighting/pixel_strips_validators.py
from __future__ import annotations

from typing import Any, Dict, List

from helpers.validation import (
    ValidationError,
    ensure_dict,
    ensure_float,
    ensure_int,
    ensure_list,
    ensure_list_of_dicts,
    ensure_list_of_str,
    ensure_str,
)


def validate_pixel_strips_doc(
    raw: Any,
    *,
    schema_name: str = "pixel_strips",
    schema_version: int = 1,
) -> Dict[str, Any]:
    """
    Validate a pixel strips document.

    Returns the original raw dict on success, otherwise raises ValidationError.
    """
    doc = ensure_dict(raw, path="pixel_strips")
    name = ensure_str(doc.get("schema_name", ""), path="pixel_strips.schema_name")
    if name != schema_name:
        raise ValidationError(
            f"pixel_strips.schema_name must be {schema_name!r} (got {name!r})"
        )

    version = ensure_int(
        doc.get("schema_version", None),
        path="pixel_strips.schema_version",
        min_v=1,
    )
    if version != schema_version:
        raise ValidationError(
            f"pixel_strips.schema_version must be {schema_version} (got {version})"
        )

    strips = ensure_list_of_dicts(doc.get("strips", None), path="pixel_strips.strips")

    ids: set[str] = set()
    for i, strip in enumerate(strips):
        _validate_strip(strip, path=f"pixel_strips.strips[{i}]", ids=ids)

    return doc


def _validate_strip(strip: Dict[str, Any], *, path: str, ids: set[str]) -> None:
    strip_id = ensure_str(strip.get("id", ""), path=f"{path}.id")
    if strip_id in ids:
        raise ValidationError(f"duplicate strip id {strip_id!r} at {path}")
    ids.add(strip_id)

    ensure_str(strip.get("type", ""), path=f"{path}.type")

    pixel_count = ensure_int(strip.get("pixel_count", None), path=f"{path}.pixel_count", min_v=0)
    pixels = ensure_list(strip.get("pixels", None), path=f"{path}.pixels")
    if len(pixels) != pixel_count:
        raise ValidationError(
            f"{path}.pixels length must match pixel_count ({pixel_count}), got {len(pixels)}"
        )

    for j, triplet in enumerate(pixels):
        trip = ensure_list(triplet, path=f"{path}.pixels[{j}]")
        if len(trip) != 3:
            raise ValidationError(f"{path}.pixels[{j}] must be an RGB triplet")
        for k, val in enumerate(trip):
            ensure_int(val, path=f"{path}.pixels[{j}][{k}]", min_v=0, max_v=255)

    ensure_float(
        strip.get("master_brightness", 1.0),
        path=f"{path}.master_brightness",
        min_v=0.0,
        max_v=1.0,
    )

    names = ensure_dict(strip.get("names", None), path=f"{path}.names")
    ensure_str(names.get("display", ""), path=f"{path}.names.display", allow_empty=True)
    ensure_list_of_str(names.get("aliases", []), path=f"{path}.names.aliases")

    if "endpoint" in strip and strip["endpoint"] is not None:
        _validate_endpoint(strip["endpoint"], path=f"{path}.endpoint")

    if "placement" in strip and strip["placement"] is not None:
        ensure_str(strip["placement"], path=f"{path}.placement", allow_empty=False)


def _validate_endpoint(raw: Any, *, path: str) -> None:
    endpoint = ensure_dict(raw, path=path)
    ensure_str(endpoint.get("kind", ""), path=f"{path}.kind")

    if "host" in endpoint and endpoint["host"] is not None:
        ensure_str(endpoint["host"], path=f"{path}.host")

    if "port" in endpoint and endpoint["port"] is not None:
        ensure_int(endpoint["port"], path=f"{path}.port", min_v=0, max_v=65535)

    if "path" in endpoint and endpoint["path"] is not None:
        ensure_str(endpoint["path"], path=f"{path}.path")

    if "meta" in endpoint and endpoint["meta"] is not None:
        ensure_dict(endpoint["meta"], path=f"{path}.meta")
