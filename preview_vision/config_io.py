# preview_vision/config_io.py
# Load + validate a vision capture config (source driver + params), then build a FrameSource via driver registry.

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from helpers.fs import read_json_strict
from helpers.validation import ValidationError
from helpers.vision.config.schema import VisionConfig, ensure_vision_config
from helpers.vision.drivers import make_source
from helpers.vision.source import FrameSource


@dataclass(frozen=True)
class CaptureConfig:
    """
    Minimal capture config extracted from VisionConfig.

    We only use:
      pipeline.source.driver
      pipeline.source.params
    """
    driver: str
    params: Dict[str, Any]


def load_vision_config(path: Path) -> VisionConfig:
    """
    Load a JSON file and validate it as a VisionConfig.

    Raises ValidationError on parse/type/schema problems.
    """
    raw = read_json_strict(path, root_types=(dict,))
    return ensure_vision_config(raw, path="vision")


def capture_config_from_vision(cfg: VisionConfig) -> CaptureConfig:
    """Extract (driver, params) from a validated VisionConfig."""
    return CaptureConfig(driver=cfg.pipeline.source.driver, params=dict(cfg.pipeline.source.params))


def build_source_from_config(cfg: CaptureConfig) -> FrameSource:
    """Instantiate a FrameSource using the helpers.vision.drivers registry."""
    return make_source(cfg.driver, cfg.params)
