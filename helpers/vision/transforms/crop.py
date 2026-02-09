# helpers/vision/transforms/crop.py
# Frame-level crop transforms (thin wrappers over helpers.transforms.imaging).

from __future__ import annotations

from typing import Iterable

from helpers.transforms.imaging import crop_xyxy_px_np, crop_rect_norm_np

from ..frame import Frame


def crop_xyxy_px(frame: Frame, xyxy_px: Iterable[float]) -> Frame:
    """
    Crop in pixel space.

    Delegates to helpers.transforms.imaging.crop_xyxy_px_np.
    This wrapper records metadata about the operation on the Frame.
    """
    before = (frame.w, frame.h)
    xyxy_t = tuple(float(v) for v in xyxy_px)
    img2 = crop_xyxy_px_np(frame.image, xyxy_t)
    after = (int(img2.shape[1]), int(img2.shape[0]))
    return frame.with_image(img2, crop_xyxy_px=xyxy_t, size_before=before, size_after=after)


def crop_rect_norm(frame: Frame, xyxy_norm: Iterable[float]) -> Frame:
    """
    Crop in normalized space ([0..1]).

    Delegates to helpers.transforms.imaging.crop_rect_norm_np.
    This wrapper records metadata about the operation on the Frame.
    """
    before = (frame.w, frame.h)
    xyxy_t = tuple(float(v) for v in xyxy_norm)
    img2 = crop_rect_norm_np(frame.image, xyxy_t)
    after = (int(img2.shape[1]), int(img2.shape[0]))
    return frame.with_image(img2, crop_xyxy_norm=xyxy_t, size_before=before, size_after=after)
