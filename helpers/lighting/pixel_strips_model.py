from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple


# -------------------------
# Core value objects
# -------------------------

@dataclass(frozen=True, slots=True)
class PixelColorRGB:
    """RGB color (0..255 each)."""
    r: int
    g: int
    b: int

    def __post_init__(self) -> None:
        for name, v in (("r", self.r), ("g", self.g), ("b", self.b)):
            if not isinstance(v, int):
                raise TypeError(f"{name} must be int, got {type(v).__name__}")
            if v < 0 or v > 255:
                raise ValueError(f"{name} must be 0..255, got {v}")

    @staticmethod
    def black() -> "PixelColorRGB":
        return PixelColorRGB(0, 0, 0)

    def to_triplet(self) -> List[int]:
        return [self.r, self.g, self.b]

    @staticmethod
    def from_triplet(t: Sequence[int]) -> "PixelColorRGB":
        if len(t) != 3:
            raise ValueError("RGB triplet must have length 3")
        return PixelColorRGB(int(t[0]), int(t[1]), int(t[2]))


class StripType(str, Enum):
    WLED = "wled"
    VISUALIZER = "visualizer"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class Endpoint:
    """
    Generic routing descriptor.

    Examples:
      Endpoint(kind="ddp", host="192.168.1.50", port=4048)
      Endpoint(kind="visualizer", path="main")
    """
    kind: str
    host: Optional[str] = None
    port: Optional[int] = None
    path: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

    def to_raw(self) -> Dict[str, Any]:
        raw: Dict[str, Any] = {"kind": self.kind}
        if self.host is not None:
            raw["host"] = self.host
        if self.port is not None:
            raw["port"] = int(self.port)
        if self.path is not None:
            raw["path"] = self.path
        if self.meta is not None:
            raw["meta"] = self.meta
        return raw

    @staticmethod
    def from_raw(raw: Dict[str, Any]) -> "Endpoint":
        return Endpoint(
            kind=str(raw.get("kind", "")),
            host=raw.get("host", None),
            port=(int(raw["port"]) if "port" in raw and raw["port"] is not None else None),
            path=raw.get("path", None),
            meta=(raw.get("meta", None) if isinstance(raw.get("meta", None), dict) else None),
        )


# -------------------------
# Document shape helpers (raw dict)
# -------------------------

def seed_pixel_strips_doc(*, schema_name: str = "pixel_strips", schema_version: int = 1) -> Dict[str, Any]:
    """
    Seed document for your catalog/persist layer.
    Keep it list-based to maximize compatibility with History list ops. 
    """
    return {
        "schema_name": schema_name,
        "schema_version": int(schema_version),
        "strips": [],  # list[strip_raw]
    }


def seed_strip_raw(
    *,
    strip_id: str,
    pixel_count: int,
    strip_type: StripType = StripType.OTHER,
    display_name: Optional[str] = None,
    aliases: Optional[List[str]] = None,
    endpoint: Optional[Endpoint] = None,
    placement: Optional[str] = None,
    master_brightness: float = 1.0,
    fill: Optional[PixelColorRGB] = None,
) -> Dict[str, Any]:
    if not strip_id:
        raise ValueError("strip_id must be non-empty")
    if pixel_count < 0:
        raise ValueError("pixel_count must be >= 0")

    fill = fill or PixelColorRGB.black()
    pixels = [fill.to_triplet() for _ in range(pixel_count)]

    raw: Dict[str, Any] = {
        "id": strip_id,
        "type": strip_type.value,
        "pixel_count": int(pixel_count),
        "pixels": pixels,
        "master_brightness": float(master_brightness),
        "names": {
            "display": display_name or "",
            "aliases": aliases or [],
        },
    }

    if endpoint is not None:
        raw["endpoint"] = endpoint.to_raw()
    if placement is not None:
        raw["placement"] = placement

    return raw


def normalize_master_brightness(x: float) -> float:
    if not isinstance(x, (int, float)):
        raise TypeError("master_brightness must be a number")
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return float(x)


def apply_master_brightness_to_rgb_triplet(rgb: Sequence[int], master_brightness: float) -> Tuple[int, int, int]:
    """
    Non-destructive brightness applied at render time.
    """
    b = normalize_master_brightness(master_brightness)
    r = max(0, min(255, int(round(int(rgb[0]) * b))))
    g = max(0, min(255, int(round(int(rgb[1]) * b))))
    bb = max(0, min(255, int(round(int(rgb[2]) * b))))
    return r, g, bb
