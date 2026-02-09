# helpers/math/__init__.py
"""helpers.math

Math helpers.

Public surface is defined by helpers.math.basic.
"""

from .basic import (
    clamp,
    clamp01,
    clamp8,
    clamp_int,
    lerp,
    inv_lerp,
    remap,
    safe_div,
    round_int,
    wrap_index,
    smoothstep,
)

__all__ = [
    "clamp",
    "clamp01",
    "clamp8",
    "clamp_int",
    "lerp",
    "inv_lerp",
    "remap",
    "safe_div",
    "round_int",
    "wrap_index",
    "smoothstep",
]
