# helpers/bytes_conv.py
from __future__ import annotations

"""
Compatibility facade for byte/frame utilities.

Historically, helpers.bytes_conv provided RGB packing and LUT/gamma utilities.
These implementations now live in helpers.transforms.bytes.rgb_frame.
This module preserves the old import surface for tests and downstream callers.
"""

from typing import Sequence

from helpers.color.color_types import ColorRGB
from helpers.transforms.bytes.rgb_frame import (
    apply_brightness_u8,
    apply_lut_u8,
    black_frame_bytes,
    make_gamma_lut_u8,
    pack_rgb_u8,
    solid_frame_bytes,
    validate_color_order,
    validate_frame_rgb,
)

__all__ = [
    "validate_color_order",
    "validate_frame_rgb",
    "pack_rgb_u8",
    "pack_rgb_tuple_u8",
    "black_frame_bytes",
    "solid_frame_bytes",
    "apply_brightness_u8",
    "apply_lut_u8",
    "build_gamma_lut",
    "apply_gamma_u8",
]


def pack_rgb_tuple_u8(r: int, g: int, b: int, order: str = "RGB") -> bytes:
    return pack_rgb_u8(ColorRGB(r, g, b), order=order)


def build_gamma_lut(gamma: float) -> list[int]:
    return make_gamma_lut_u8(gamma)


def apply_gamma_u8(frame: bytes, gamma: float) -> bytes:
    lut: Sequence[int] = make_gamma_lut_u8(gamma)
    return apply_lut_u8(frame, lut)
