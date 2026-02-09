# helpers/vision/imaging_buffers.py
# Numpy image buffer helpers for UI interop (e.g., converting RGB frames to RGBA textures).

from __future__ import annotations

"""
helpers.vision.imaging_buffers
------------------------------

Small helpers for converting numpy image buffers into formats used by UI/tooling layers.

Scope:
- lightweight array reshaping / channel expansion
- no heavy image processing (resize/crop/etc.)

Common use cases:
- DearPyGui raw textures (U8 RGBA)
- OpenGL / ImGui texture uploads
"""

from typing import Final

import numpy as np


_ALPHA_FULL: Final[int] = 255


def rgb_to_rgba_u8(rgb: np.ndarray) -> np.ndarray:
    """
    Convert HxWx3 RGB uint8 -> HxWx4 RGBA uint8 with alpha channel set to 255.

    Notes:
      - This is a pure buffer conversion; it does not change color space.
      - The returned array is a new contiguous array.

    Args:
      rgb: numpy array shaped (H, W, 3), dtype uint8.

    Returns:
      rgba: numpy array shaped (H, W, 4), dtype uint8.

    Raises:
      ValueError: if input is not uint8 HxWx3.
    """
    if not isinstance(rgb, np.ndarray):
        raise ValueError("rgb_to_rgba_u8: expected a numpy.ndarray")

    if rgb.dtype != np.uint8:
        raise ValueError(f"rgb_to_rgba_u8: expected dtype=uint8 (got {rgb.dtype})")

    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError(f"rgb_to_rgba_u8: expected shape (H,W,3) (got {rgb.shape})")

    h, w, _ = rgb.shape
    rgba = np.empty((h, w, 4), dtype=np.uint8)
    rgba[:, :, :3] = rgb
    rgba[:, :, 3] = _ALPHA_FULL
    return rgba
