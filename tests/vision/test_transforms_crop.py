# tests/vision/test_transforms_crop.py

from __future__ import annotations

import numpy as np

from helpers.vision.frame import Frame
from helpers.vision.transforms.crop import crop_rect_norm


def _frame_10x10() -> Frame:
    img = np.arange(10 * 10 * 3, dtype=np.uint8).reshape((10, 10, 3))
    return Frame(image=img, ts_monotonic=0.0)


def test_crop_rect_norm_xywh() -> None:
    frame = _frame_10x10()
    out = crop_rect_norm(frame, rect_norm=(0.2, 0.1, 0.5, 0.4))

    assert out.image.shape[:2] == (4, 5)
    assert out.meta["crop_xyxy_norm"] == (0.2, 0.1, 0.7, 0.5)


def test_crop_rect_norm_xyxy() -> None:
    frame = _frame_10x10()
    out = crop_rect_norm(frame, xyxy_norm=(0.2, 0.1, 0.7, 0.5))

    assert out.image.shape[:2] == (4, 5)
    assert out.meta["crop_xyxy_norm"] == (0.2, 0.1, 0.7, 0.5)
