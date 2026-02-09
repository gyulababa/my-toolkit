# helpers/zones/__init__.py
"""helpers.zones

Agnostic "zones preset library" schema + editor helpers.

This package is frontend-agnostic and does not import UI toolkits or capture/OCR libraries.
"""

from .types import (
    SchemaVersion,
    Intent,
    GeometryType,
    ZoneKey,
    PresetId,
)

from .schema import (
    ensure_library_shape,
    ensure_zone_shape,
    ensure_geometry_shape,
)

from .editor import (
    ZonesEditor,
)

# Convenience re-exports for common geometry usage in zone editors/renderers.
from helpers.geometry import (
    normalize_xyxy,
    xyxy_is_valid,
    clamp_xyxy_to_bounds,
    clamp_xyxy_preserve_size,
    xyxy_px_to_norm,
    xyxy_norm_to_px,
)

__all__ = [
    "SchemaVersion",
    "Intent",
    "GeometryType",
    "ZoneKey",
    "PresetId",
    "ensure_library_shape",
    "ensure_zone_shape",
    "ensure_geometry_shape",
    "ZonesEditor",
    "normalize_xyxy",
    "xyxy_is_valid",
    "clamp_xyxy_to_bounds",
    "clamp_xyxy_preserve_size",
    "xyxy_px_to_norm",
    "xyxy_norm_to_px",
]
