# tests/test_transforms_imaging_colors.py
from __future__ import annotations

import numpy as np

from helpers.transforms.imaging import ensure_rgb8_np, bgr_to_rgb_np, gray_to_rgb_np


def test_bgr_to_rgb_np_swaps_channels() -> None:
    # BGR pixel: (10,20,30) => RGB should become (30,20,10)
    img = np.array([[[10, 20, 30]]], dtype=np.uint8)
    out = bgr_to_rgb_np(img)
    assert out.shape == (1, 1, 3)
    assert out[0, 0, 0] == 30
    assert out[0, 0, 1] == 20
    assert out[0, 0, 2] == 10


def test_gray_to_rgb_np_expands() -> None:
    img = np.array([[7, 9]], dtype=np.uint8)  # (H,W)
    out = gray_to_rgb_np(img)
    assert out.shape == (1, 2, 3)
    assert (out[0, 0] == np.array([7, 7, 7], dtype=np.uint8)).all()


def test_ensure_rgb8_np_from_gray() -> None:
    img = np.array([[1, 2], [3, 4]], dtype=np.uint8)
    out, fmt = ensure_rgb8_np(img, src_fmt="gray8")
    assert fmt == "rgb8"
    assert out.shape == (2, 2, 3)


def test_ensure_rgb8_np_from_bgr() -> None:
    img = np.array([[[0, 1, 2]]], dtype=np.uint8)  # B,G,R
    out, fmt = ensure_rgb8_np(img, src_fmt="bgr8")
    assert fmt == "rgb8"
    assert (out[0, 0] == np.array([2, 1, 0], dtype=np.uint8)).all()


def test_ensure_rgb8_np_auto_keeps_rgb_like() -> None:
    img = np.array([[[5, 6, 7]]], dtype=np.uint8)
    out, fmt = ensure_rgb8_np(img, src_fmt="auto")
    assert fmt == "rgb8"
    assert out.shape == (1, 1, 3)
