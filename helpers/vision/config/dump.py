# helpers/vision/config/dump.py
from __future__ import annotations

from typing import Any, Dict

from .schema import VisionConfig


def dump_vision_config(cfg: VisionConfig) -> Dict[str, Any]:
    return {
        "schema_version": int(cfg.schema_version),
        "pipeline": {
            "source": {
                "driver": cfg.pipeline.source.driver,
                "params": dict(cfg.pipeline.source.params),
            },
            "transforms": [
                {"name": t.name, "params": dict(t.params)}
                for t in cfg.pipeline.transforms
            ],
        },
    }
