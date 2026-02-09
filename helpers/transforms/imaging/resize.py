# helpers/transforms/imaging/resize.py
from __future__ import annotations

"""
helpers.transforms.imaging.resize
---------------------------------

Pure numpy resizing helpers (nearest-neighbor).

- No cv2/PIL dependency.
- Uses helpers.geometry.rect.fit_aspect for aspect preservation.
"""

from typing import Literal, Tuple

import numpy as np

from helpers.geometry.rect import fit_aspect


def _resize_nearest_np(img: np.ndarray, new_w: int, new_h: int) -> np.ndarray:
    """
    Nearest-neighbor resize (pure numpy).

    Notes:
    - Works for (H,W) and (H,W,C)
    - Returns a copy
    """
    if img.ndim < 2:
        return img

    h, w = int(img.shape[0]), int(img.shape[1])
    if new_w <= 0 or new_h <= 0:
        return img
    if new_w == w and new_h == h:
        return img.copy()

    ys = (np.linspace(0, h - 1, new_h)).astype(np.int32)
    xs = (np.linspace(0, w - 1, new_w)).astype(np.int32)

    if img.ndim == 2:
        return img[ys][:, xs].copy()
    return img[ys][:, xs, :].copy()


def resize_max_np(img: np.ndarray, *, max_w: int, max_h: int) -> np.ndarray:
    """
    Resize down to fit within (max_w, max_h), preserving aspect ratio.

    If already within bounds => returns a copy of the original.
    """
    if img.ndim < 2:
        return img

    h, w = int(img.shape[0]), int(img.shape[1])
    if w <= 0 or h <= 0:
        return img

    if w <= max_w and h <= max_h:
        return img.copy()

    _, _, fw, fh = fit_aspect(w, h, max_w, max_h, mode="contain")
    new_w, new_h = int(round(fw)), int(round(fh))
    return _resize_nearest_np(img, new_w, new_h)


def resize_fit_aspect_np(
    img: np.ndarray,
    *,
    dst_w: int,
    dst_h: int,
    mode: Literal["contain", "cover"] = "contain",
) -> np.ndarray:
    """
    Resize preserving aspect to fit into a destination size.

    Returns the resized image sized to the fitted rect:
      - contain => smaller rect
      - cover   => larger rect

    Does not pad/crop; caller can crop/pad after.
    """
    if img.ndim < 2:
        return img

    h, w = int(img.shape[0]), int(img.shape[1])
    if w <= 0 or h <= 0 or dst_w <= 0 or dst_h <= 0:
        return img

    _, _, fw, fh = fit_aspect(w, h, dst_w, dst_h, mode=mode)
    new_w, new_h = int(round(fw)), int(round(fh))
    return _resize_nearest_np(img, new_w, new_h)
