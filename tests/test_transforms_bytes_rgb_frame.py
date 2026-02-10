# tests/test_transforms_bytes_rgb_frame.py
from __future__ import annotations

import pytest

from helpers.color.color_types import ColorRGB
from helpers.transforms.bytes import (
    validate_color_order,
    validate_frame_rgb,
    pack_rgb_u8,
    black_frame_bytes,
    solid_frame_bytes,
    apply_brightness_u8,
    apply_lut_u8,
    make_gamma_lut_u8,
)


def test_validate_color_order_accepts() -> None:
    assert validate_color_order("RGB") == "RGB"
    assert validate_color_order("GRB") == "GRB"


def test_validate_color_order_rejects() -> None:
    with pytest.raises(ValueError):
        validate_color_order("XYZ")


def test_pack_rgb_u8_orders() -> None:
    c = ColorRGB(1, 2, 3)
    assert pack_rgb_u8(c, "RGB") == bytes([1, 2, 3])
    assert pack_rgb_u8(c, "BGR") == bytes([3, 2, 1])
    assert pack_rgb_u8(c, "GRB") == bytes([2, 1, 3])


def test_black_frame_bytes() -> None:
    b = black_frame_bytes(4)
    assert len(b) == 12
    assert set(b) == {0}


def test_solid_frame_bytes() -> None:
    b = solid_frame_bytes(3, ColorRGB(9, 8, 7), order="RGB")
    assert len(b) == 9
    assert b == bytes([9, 8, 7]) * 3


def test_validate_frame_rgb_len_multiple_of_3() -> None:
    validate_frame_rgb(bytes([0, 0, 0]))
    with pytest.raises(ValueError):
        validate_frame_rgb(bytes([0, 0]))


def test_apply_brightness_u8_identity_and_zero() -> None:
    frame = bytes([10, 20, 30, 40, 50, 60])
    assert apply_brightness_u8(frame, 1.0) == frame
    assert apply_brightness_u8(frame, 0.0) == bytes([0]) * len(frame)


def test_apply_brightness_u8_scales() -> None:
    frame = bytes([10, 20, 30])
    out = apply_brightness_u8(frame, 0.5)
    # round() behavior: 10*0.5=5, 20*0.5=10, 30*0.5=15
    assert out == bytes([5, 10, 15])


def test_apply_lut_u8_identity() -> None:
    frame = bytes([0, 10, 255])
    lut = list(range(256))
    out = apply_lut_u8(frame, lut)
    assert out == frame


def test_make_gamma_lut_u8_properties() -> None:
    lut = make_gamma_lut_u8(1.0)
    assert len(lut) == 256
    assert lut[0] == 0
    assert lut[255] == 255
