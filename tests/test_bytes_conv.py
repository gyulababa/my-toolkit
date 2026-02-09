# tests/test_bytes_conv.py
from __future__ import annotations

import pytest

# NOTE:
# bytes_conv imports ColorRGB from project-specific locations in your tree.
# If those imports are already correct in your project, remove the stubs and
# import normally. These tests assume the module is importable.
from helpers.bytes_conv import (
    validate_color_order,
    validate_frame_rgb,
    pack_rgb_u8,
    pack_rgb_tuple_u8,
    black_frame_bytes,
    solid_frame_bytes,
    apply_brightness_u8,
    apply_lut_u8,
    build_gamma_lut,
    apply_gamma_u8,
)

from helpers.color.color_types import ColorRGB


def test_validate_color_order():
    assert validate_color_order("RGB") == "RGB"
    with pytest.raises(ValueError):
        validate_color_order("NOPE")


def test_validate_frame_rgb():
    validate_frame_rgb(b"\x00\x01\x02")
    with pytest.raises(ValueError):
        validate_frame_rgb(b"\x00\x01")  # not multiple of 3
    with pytest.raises(TypeError):
        validate_frame_rgb("not-bytes")  # type: ignore


def test_pack_rgb_u8_orders():
    c = ColorRGB(1, 2, 3)
    assert pack_rgb_u8(c, "RGB") == bytes([1, 2, 3])
    assert pack_rgb_u8(c, "GRB") == bytes([2, 1, 3])
    assert pack_rgb_tuple_u8(1, 2, 3, "BGR") == bytes([3, 2, 1])


def test_black_and_solid_frames():
    assert black_frame_bytes(2) == b"\x00" * 6
    c = ColorRGB(10, 20, 30)
    f = solid_frame_bytes(3, c, order="RGB")
    assert len(f) == 9
    assert f == bytes([10, 20, 30]) * 3


def test_apply_brightness():
    base = bytes([10, 20, 30]) * 2
    off = apply_brightness_u8(base, 0.0)
    assert off == b"\x00" * len(base)

    same = apply_brightness_u8(base, 1.0)
    assert same == base

    half = apply_brightness_u8(base, 0.5)
    assert half == bytes([5, 10, 15]) * 2


def test_apply_lut_and_gamma():
    base = bytes([0, 128, 255]) * 2
    lut = bytes(range(256))
    out = apply_lut_u8(base, lut)
    assert out == base

    g = build_gamma_lut(2.2)
    assert len(g) == 256
    out2 = apply_gamma_u8(base, 2.2)
    assert len(out2) == len(base)
