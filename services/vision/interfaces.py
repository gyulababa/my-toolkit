# services/vision/interfaces.py
# Shared wiring interfaces for vision services (frontend-agnostic).

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

from helpers.vision.source import FrameSource


class CaptureConfigLike(Protocol):
    driver: str
    params: Mapping[str, Any]


VisionConfigLoader = Callable[[Path], Any]
CaptureConfigBuilder = Callable[[Any], CaptureConfigLike]
FrameSourceBuilder = Callable[[CaptureConfigLike], FrameSource]
