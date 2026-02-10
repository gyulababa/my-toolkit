# tests/test_transforms_imaging_crop.py
from __future__ import annotations

import numpy as np

from helpers.transforms.imaging import crop_xyxy_px_np, crop_rect_norm_np


def test_crop_xyxy_px_np_basic() -> None:
    img = np.arange(10 * 10 * 3, dtype=np.uint8).reshape(10, 10, 3)
    out = crop_xyxy_px_np(img, (2, 3, 7, 9))
    assert out.shape == (6, 5, 3)  # y: 3..9 => 6, x: 2..7 => 5


def test_crop_xyxy_px_np_clamps() -> None:
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    out = crop_xyxy_px_np(img, (-5, -5, 50, 50))
    assert out.shape == (10, 10, 3)


def test_crop_xyxy_px_np_empty_returns_original_object_or_copy_ok() -> None:
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    out = crop_xyxy_px_np(img, (5, 5, 5, 9))  # empty width
    assert out.shape == img.shape


def test_crop_rect_norm_np_basic() -> None:
    img = np.zeros((100, 200, 3), dtype=np.uint8)
    out = crop_rect_norm_np(img, (0.25, 0.1, 0.75, 0.6))
    # x: 50..150 => 100; y: 10..60 => 50
    assert out.shape == (50, 100, 3)


def test_crop_rect_norm_np_clamps_to_unit() -> None:
    img = np.zeros((100, 200, 3), dtype=np.uint8)
    out = crop_rect_norm_np(img, (-1, -1, 2, 2))
    assert out.shape == img.shape
