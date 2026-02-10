# tests/test_transforms_imaging_resize.py
from __future__ import annotations

import numpy as np

from helpers.transforms.imaging import resize_max_np, resize_fit_aspect_np


def test_resize_max_np_noop_within_bounds_returns_copy() -> None:
    img = np.zeros((10, 20, 3), dtype=np.uint8)
    out = resize_max_np(img, max_w=50, max_h=50)
    assert out.shape == img.shape
    # should be safe to mutate out without changing img if it's a copy
    out[0, 0, 0] = 255
    assert img[0, 0, 0] == 0


def test_resize_max_np_downscale_preserves_aspect() -> None:
    img = np.zeros((100, 200, 3), dtype=np.uint8)  # aspect 2.0
    out = resize_max_np(img, max_w=50, max_h=50)
    # contain inside 50x50 => width hits 50, height becomes 25
    assert out.shape == (25, 50, 3)


def test_resize_fit_aspect_np_contain() -> None:
    img = np.zeros((100, 200, 3), dtype=np.uint8)  # aspect 2.0
    out = resize_fit_aspect_np(img, dst_w=60, dst_h=60, mode="contain")
    # contain => width 60, height 30
    assert out.shape == (30, 60, 3)


def test_resize_fit_aspect_np_cover() -> None:
    img = np.zeros((100, 200, 3), dtype=np.uint8)  # aspect 2.0
    out = resize_fit_aspect_np(img, dst_w=60, dst_h=60, mode="cover")
    # cover => height 60, width 120
    assert out.shape == (60, 120, 3)
