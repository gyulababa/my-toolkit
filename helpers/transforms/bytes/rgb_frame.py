# helpers/transforms/bytes/rgb_frame.py
from __future__ import annotations

"""
helpers.transforms.bytes.rgb_frame
----------------------------------

Byte-oriented transforms for packed RGB LED frame payloads.

Scope:
- RGB (3 bytes per pixel) packing with configurable channel order (RGB/GRB/etc.)
- Frame constructors (black/solid)
- Validation (bytes-like, len % 3 == 0)
- Per-byte transforms (brightness scaling, LUT, gamma LUT)

Non-goals:
- Protocol logic (WLED/DDP) -> belongs in helpers.toolkits / drivers
- Color management beyond basic gamma LUT

Note:
- Uses helpers.color.color_types.ColorRGB as the canonical color type.
"""

from typing import Sequence

from helpers.color.color_types import ColorRGB
from helpers.math.basic import clamp01, clamp8

# Canonical channel orders supported for RGB (3 bytes per pixel).
ALLOWED_COLOR_ORDERS: tuple[str, ...] = ("RGB", "RBG", "GRB", "GBR", "BRG", "BGR")

_ORDER_INDEX: dict[str, tuple[int, int, int]] = {
    "RGB": (0, 1, 2),
    "RBG": (0, 2, 1),
    "GRB": (1, 0, 2),
    "GBR": (1, 2, 0),
    "BRG": (2, 0, 1),
    "BGR": (2, 1, 0),
}

# ─────────────────────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────────────────────

def validate_color_order(order: str) -> str:
    """
    Validate and return the order string.

    Raises:
      ValueError if order is not one of ALLOWED_COLOR_ORDERS.
    """
    if order not in _ORDER_INDEX:
        raise ValueError(f"color_order must be one of {list(ALLOWED_COLOR_ORDERS)} (got {order!r})")
    return order


def validate_frame_rgb(frame: bytes) -> None:
    """
    Validate that a frame looks like packed RGB bytes.

    Requirements:
    - frame is bytes-like
    - len(frame) is a multiple of 3 (3 bytes per pixel)
    """
    if not isinstance(frame, (bytes, bytearray, memoryview)):
        raise TypeError(f"frame must be bytes-like (got {type(frame).__name__})")
    if len(frame) % 3 != 0:
        raise ValueError(f"RGB frame length must be multiple of 3 (got {len(frame)})")


# ─────────────────────────────────────────────────────────────
# Packing and frame construction
# ─────────────────────────────────────────────────────────────

def pack_rgb_u8(color: ColorRGB, order: str = "RGB") -> bytes:
    """
    Pack a ColorRGB into 3 bytes in the requested channel order.

    Clamping occurs here to keep ColorRGB as a simple value object.
    """
    validate_color_order(order)
    r = clamp8(color.r)
    g = clamp8(color.g)
    b = clamp8(color.b)

    idx = _ORDER_INDEX[order]
    ch = (r, g, b)
    return bytes((ch[idx[0]], ch[idx[1]], ch[idx[2]]))


def black_frame_bytes(pixel_count: int) -> bytes:
    """
    Build a black RGB frame (all zeros) for N pixels.
    """
    if pixel_count < 0:
        raise ValueError("pixel_count must be >= 0")
    return bytes([0]) * (pixel_count * 3)


def solid_frame_bytes(pixel_count: int, color: ColorRGB, order: str = "RGB") -> bytes:
    """
    Build a solid color frame for N pixels in the given channel order.
    """
    if pixel_count < 0:
        raise ValueError("pixel_count must be >= 0")
    px = pack_rgb_u8(color, order=order)
    return px * pixel_count


# ─────────────────────────────────────────────────────────────
# Per-byte transforms
# ─────────────────────────────────────────────────────────────

def apply_brightness_u8(frame: bytes, brightness: float) -> bytes:
    """
    Multiply every byte by brightness in [0..1].

    Note:
    This is byte-level scaling (not perceptual). For better appearance,
    combine with a gamma LUT.
    """
    validate_frame_rgb(frame)
    b = clamp01(brightness)
    if b == 1.0:
        return bytes(frame)
    if b == 0.0:
        return bytes([0]) * len(frame)

    out = bytearray(len(frame))
    for i, v in enumerate(frame):
        out[i] = clamp8(int(round(v * b)))
    return bytes(out)


def apply_lut_u8(frame: bytes, lut: Sequence[int]) -> bytes:
    """
    Apply a 256-entry LUT to every byte.
    """
    validate_frame_rgb(frame)
    if len(lut) != 256:
        raise ValueError(f"lut must have length 256 (got {len(lut)})")

    out = bytearray(len(frame))
    for i, v in enumerate(frame):
        out[i] = clamp8(int(lut[v]))
    return bytes(out)


def make_gamma_lut_u8(gamma: float) -> list[int]:
    """
    Create a gamma correction LUT for u8 values.

    gamma:
      - 1.0 => identity
      - >1  => darker mid-tones
      - <1  => brighter mid-tones
    """
    if gamma <= 0:
        raise ValueError("gamma must be > 0")

    lut: list[int] = [0] * 256
    for i in range(256):
        x = i / 255.0
        y = pow(x, gamma)
        lut[i] = clamp8(int(round(y * 255.0)))
    return lut
