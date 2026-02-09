# helpers/vision/config/schema.py
# Validation schema for vision pipeline configuration (delegates to helpers.validation).

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from helpers.validation import ValidationError, ensure_dict, ensure_str


@dataclass(frozen=True)
class VisionSourceConfig:
    """Validated config for the source/driver section."""
    driver: str
    params: Dict[str, Any]


@dataclass(frozen=True)
class VisionTransformConfig:
    """Validated config for a single transform entry."""
    name: str
    params: Dict[str, Any]


@dataclass(frozen=True)
class VisionPipelineConfig:
    """Validated config for the vision pipeline (source + transforms)."""
    source: VisionSourceConfig
    transforms: List[VisionTransformConfig]


@dataclass(frozen=True)
class VisionConfig:
    """Top-level validated vision config document."""
    schema_version: int
    pipeline: VisionPipelineConfig


def ensure_vision_config(raw: Any, *, path: str = "vision") -> VisionConfig:
    """
    Validate and normalize a vision config document.

    Current schema:
      schema_version: 1
      pipeline:
        source:
          driver: str
          params: dict (optional, default {})
        transforms: list[{name:str, params:dict}] (optional, default [])
    """
    d = ensure_dict(raw, path=path)

    sv = d.get("schema_version")
    if sv != 1:
        raise ValidationError(f"{path}.schema_version must be 1 (got {sv!r})")

    p = ensure_dict(d.get("pipeline"), path=f"{path}.pipeline")

    src = ensure_dict(p.get("source"), path=f"{path}.pipeline.source")
    driver = ensure_str(src.get("driver"), path=f"{path}.pipeline.source.driver")
    params = ensure_dict(src.get("params", {}), path=f"{path}.pipeline.source.params")

    # transforms list is optional (defaults to [])
    tlist_raw = p.get("transforms", [])
    if not isinstance(tlist_raw, list):
        raise ValidationError(f"{path}.pipeline.transforms must be a list (got {type(tlist_raw).__name__})")

    transforms: List[VisionTransformConfig] = []
    for i, tr in enumerate(tlist_raw):
        td = ensure_dict(tr, path=f"{path}.pipeline.transforms[{i}]")
        name = ensure_str(td.get("name"), path=f"{path}.pipeline.transforms[{i}].name")
        tparams = ensure_dict(td.get("params", {}), path=f"{path}.pipeline.transforms[{i}].params")
        transforms.append(VisionTransformConfig(name=name, params=tparams))

    return VisionConfig(
        schema_version=1,
        pipeline=VisionPipelineConfig(
            source=VisionSourceConfig(driver=driver, params=params),
            transforms=transforms,
        ),
    )
