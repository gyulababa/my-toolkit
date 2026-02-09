# helpers/vision/drivers/registry.py
# Driver registry for helpers.vision: maps driver names to FrameSource factories (frontend-agnostic).

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional

from helpers.validation.errors import ValidationError
from helpers.validation.scalars import ensure_float, ensure_int, ensure_str

from ..source import FrameSource
from .screen_mss import ScreenMssSource
from .uvc_opencv import UvcOpenCvSource


Factory = Callable[[Mapping[str, Any]], FrameSource]


@dataclass(frozen=True)
class DriverSpec:
    """Metadata about a registered driver."""
    name: str
    summary: str


_REGISTRY: Dict[str, Factory] = {}
_SPECS: Dict[str, DriverSpec] = {}


def register_driver(name: str, factory: Factory, *, summary: str) -> None:
    """Register a new driver factory under a stable name."""
    key = (name or "").strip()
    if not key:
        raise ValueError("register_driver: name must be non-empty")
    _REGISTRY[key] = factory
    _SPECS[key] = DriverSpec(name=key, summary=summary)


def list_drivers() -> list[DriverSpec]:
    """List known drivers (name + summary)."""
    return [*_SPECS.values()]


def list_driver_names() -> list[str]:
    """List known driver names."""
    return sorted(_REGISTRY.keys())


def make_source(name: str, params: Optional[Mapping[str, Any]] = None) -> FrameSource:
    """
    Create a FrameSource from a driver name + params mapping.

    Raises ValidationError if driver name is unknown or params is not a mapping.
    """
    if not isinstance(name, str) or not name.strip():
        raise ValidationError("driver must be a non-empty string")

    if params is None:
        params = {}

    if not isinstance(params, Mapping):
        raise ValidationError(f"params must be a mapping/dict (got {type(params).__name__})")

    fn = _REGISTRY.get(name)
    if fn is None:
        raise ValidationError(f"Unknown capture driver: {name!r}. Available: {list_driver_names()}")
    return fn(params)


# ------------------------
# Built-in factories
# ------------------------

def _make_screen_mss(p: Mapping[str, Any]) -> FrameSource:
    monitor = ensure_int(p.get("monitor", 1), path="params.monitor", min_v=0)

    target_fps = p.get("target_fps", None)
    if target_fps is not None:
        target_fps = ensure_float(target_fps, path="params.target_fps", min_v=0.1)

    return ScreenMssSource(monitor=monitor, target_fps=target_fps)


def _make_uvc_opencv(p: Mapping[str, Any]) -> FrameSource:
    device_index = ensure_int(p.get("device_index", 0), path="params.device_index", min_v=0)

    width = p.get("width", None)
    if width is not None:
        width = ensure_int(width, path="params.width", min_v=1)

    height = p.get("height", None)
    if height is not None:
        height = ensure_int(height, path="params.height", min_v=1)

    fps = p.get("fps", None)
    if fps is not None:
        fps = ensure_float(fps, path="params.fps", min_v=0.1)

    fourcc = p.get("fourcc", None)
    if fourcc is not None:
        fourcc = ensure_str(fourcc, path="params.fourcc").strip()
        if fourcc == "" or fourcc.lower() in ("none", "auto", "default"):
            fourcc = None

    buffersize = p.get("buffersize", None)
    if buffersize is not None:
        buffersize = ensure_int(buffersize, path="params.buffersize", min_v=0)

    target_fps = p.get("target_fps", None)
    if target_fps is not None:
        target_fps = ensure_float(target_fps, path="params.target_fps", min_v=0.1)

    backend_v = p.get("backend", None)
    backend: Optional[int | str]
    if backend_v is None:
        backend = None
    elif isinstance(backend_v, int):
        backend = ensure_int(backend_v, path="params.backend", min_v=0)
    elif isinstance(backend_v, str):
        backend = ensure_str(backend_v, path="params.backend").strip()
        if backend == "" or backend.lower() in ("none", "auto", "default"):
            backend = None
    else:
        raise ValidationError(f"params.backend must be int|str|null (got {type(backend_v).__name__})")

    return UvcOpenCvSource(
        device_index=device_index,
        width=width,
        height=height,
        fps=fps,
        fourcc=fourcc,
        buffersize=buffersize,
        target_fps=target_fps,
        backend=backend,
    )


# Register built-ins (import-time)
register_driver(
    "screen_mss",
    _make_screen_mss,
    summary="Screen capture via mss (Windows GDI; may be unstable on some Python/OpenCV builds).",
)
register_driver(
    "uvc_opencv",
    _make_uvc_opencv,
    summary="UVC camera capture via OpenCV VideoCapture.",
)
