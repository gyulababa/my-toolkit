# helpers/transforms/imaging/crop.py
from __future__ import annotations

"""
helpers.transforms.imaging.crop
-------------------------------

Pure numpy crop helpers.

- No dependency on helpers.vision.Frame
- No metadata / side effects
- Uses helpers.geometry.rect for xyxy normalization and clamping
"""

from typing import Iterable, Tuple

import numpy as np

from helpers.geometry.rect import normalize_xyxy, clamp_xyxy_to_bounds


def crop_xyxy_px_np(img: np.ndarray, xyxy_px: Iterable[float]) -> np.ndarray:
    """
    Crop an image with pixel-space xyxy.

    Policy:
    - xyxy is normalized (x0<=x1, y0<=y1)
    - clamped to image bounds
    - if crop becomes empty, returns the original image unchanged
    """
    if img.ndim < 2:
        return img

    h, w = int(img.shape[0]), int(img.shape[1])
    x0, y0, x1, y1 = normalize_xyxy(xyxy_px)
    x0, y0, x1, y1 = clamp_xyxy_to_bounds((x0, y0, x1, y1), min_x=0, min_y=0, max_x=w, max_y=h)

    ix0, iy0, ix1, iy1 = int(x0), int(y0), int(x1), int(y1)
    if ix1 <= ix0 or iy1 <= iy0:
        return img

    return img[iy0:iy1, ix0:ix1].copy()


def crop_rect_norm_np(img: np.ndarray, xyxy_norm: Iterable[float]) -> np.ndarray:
    """
    Crop an image using normalized xyxy (0..1). Values are clamped to [0,1].

    Policy:
    - if image has invalid size => returns original
    - if crop becomes empty => returns original
    """
    if img.ndim < 2:
        return img

    h, w = int(img.shape[0]), int(img.shape[1])
    if w <= 0 or h <= 0:
        return img

    x0n, y0n, x1n, y1n = normalize_xyxy(xyxy_norm)
    x0n, y0n, x1n, y1n = clamp_xyxy_to_bounds((x0n, y0n, x1n, y1n), min_x=0, min_y=0, max_x=1, max_y=1)

    x0 = x0n * w
    x1 = x1n * w
    y0 = y0n * h
    y1 = y1n * h
    return crop_xyxy_px_np(img, (x0, y0, x1, y1))
