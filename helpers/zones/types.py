# helpers/zones/types.py
from __future__ import annotations

from typing import Literal, NewType


SchemaVersion = Literal[1]

ZoneKey = NewType("ZoneKey", str)
PresetId = NewType("PresetId", str)

# Keep intents broad and tool-agnostic; callers may extend with custom values.
Intent = Literal[
    "Text",
    "Number",
    "Presence",
    "Queue",
    "Timer",
    "Custom",
]

GeometryType = Literal[
    "rect_px",
    "rect_norm",
]
