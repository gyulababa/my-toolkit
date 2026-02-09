from __future__ import annotations

import numpy as np

from helpers.transforms.imaging.crop import crop_rect_norm_np, crop_rect_xywh_norm_np


def test_crop_rect_norm_np_clamps_to_unit() -> None:
    img = np.zeros((100, 200, 3), dtype=np.uint8)
    out = crop_rect_norm_np(img, (-1.0, -0.5, 2.0, 1.5))
    assert out.shape == img.shape


def test_crop_rect_norm_np_empty_returns_original() -> None:
    img = np.zeros((100, 200, 3), dtype=np.uint8)
    out = crop_rect_norm_np(img, (0.4, 0.2, 0.4, 0.9))
    assert out is img


def test_crop_rect_xywh_norm_np_converts_to_xyxy() -> None:
    img = np.zeros((100, 200, 3), dtype=np.uint8)
    out = crop_rect_xywh_norm_np(img, (0.1, 0.2, 0.3, 0.4))
    assert out.shape == (40, 60, 3)


def test_crop_rect_xywh_norm_np_clamps_to_unit() -> None:
    img = np.zeros((100, 200, 3), dtype=np.uint8)
    out = crop_rect_xywh_norm_np(img, (-0.5, -0.5, 2.0, 2.0))
    assert out.shape == img.shape
