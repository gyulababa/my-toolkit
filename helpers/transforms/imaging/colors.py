# helpers/transforms/imaging/colors.py
from __future__ import annotations

"""
helpers.transforms.imaging.colors
---------------------------------

Numpy image channel conversions.

Conventions:
- "rgb8": uint8, shape (H,W,3), channels R,G,B
- "bgr8": uint8, shape (H,W,3), channels B,G,R
- "gray8": uint8, shape (H,W)
"""

from typing import Literal, Tuple

import numpy as np

PixelFmt = Literal["rgb8", "bgr8", "gray8", "auto"]


def bgr_to_rgb_np(img: np.ndarray) -> np.ndarray:
    if img.ndim == 3 and img.shape[2] == 3:
        return img[:, :, ::-1].copy()
    return img.copy()


def gray_to_rgb_np(img: np.ndarray) -> np.ndarray:
    if img.ndim == 2:
        return np.stack([img, img, img], axis=2)
    if img.ndim == 3 and img.shape[2] == 1:
        c = img[:, :, 0]
        return np.stack([c, c, c], axis=2)
    return img.copy()


def ensure_rgb8_np(img: np.ndarray, *, src_fmt: PixelFmt = "auto") -> tuple[np.ndarray, Literal["rgb8"]]:
    """
    Ensure a numpy image is RGB8 (uint8, (H,W,3)).

    Returns:
      (rgb_img, "rgb8")
    """
    if img.dtype != np.uint8:
        img = img.astype(np.uint8, copy=False)

    if src_fmt == "rgb8":
        if img.ndim == 3 and img.shape[2] == 3:
            return img.copy(), "rgb8"
        if img.ndim == 2:
            return gray_to_rgb_np(img), "rgb8"
        return img.copy(), "rgb8"

    if src_fmt == "bgr8":
        if img.ndim == 3 and img.shape[2] == 3:
            return bgr_to_rgb_np(img), "rgb8"
        if img.ndim == 2:
            return gray_to_rgb_np(img), "rgb8"
        return img.copy(), "rgb8"

    if src_fmt == "gray8":
        return gray_to_rgb_np(img), "rgb8"

    # auto
    if img.ndim == 2:
        return gray_to_rgb_np(img), "rgb8"
    if img.ndim == 3 and img.shape[2] == 3:
        # Assume already RGB (cannot reliably distinguish RGB/BGR without context)
        return img.copy(), "rgb8"
    if img.ndim == 3 and img.shape[2] == 4:
        # common BGRA/RGBA cases: drop alpha, assume it is BGRA? too risky
        rgb = img[:, :, :3].copy()
        return rgb, "rgb8"

    return img.copy(), "rgb8"
