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


def crop_rect_norm(
    frame: Frame,
    xyxy_norm: Iterable[float] | None = None,
    *,
    rect_norm: Iterable[float] | None = None,
    xywh_norm: Iterable[float] | None = None,
) -> Frame:
    """
    Crop in normalized space ([0..1]).

    Delegates to helpers.transforms.imaging.crop_rect_norm_np.
    This wrapper records metadata about the operation on the Frame.
    """
    before = (frame.w, frame.h)
    if rect_norm is not None and xywh_norm is not None:
        raise ValueError("crop_rect_norm: provide rect_norm or xywh_norm, not both")

    if rect_norm is not None or xywh_norm is not None:
        rect = rect_norm if rect_norm is not None else xywh_norm
        rect_t = tuple(float(v) for v in rect)
        if len(rect_t) != 4:
            raise ValueError("crop_rect_norm: rect_norm/xywh_norm must have 4 values")
        x, y, w, h = rect_t
        xyxy_t = (x, y, x + w, y + h)
    else:
        if xyxy_norm is None:
            raise ValueError("crop_rect_norm: xyxy_norm required when rect_norm/xywh_norm not provided")
        xyxy_t = tuple(float(v) for v in xyxy_norm)

    img2 = crop_rect_norm_np(frame.image, xyxy_t)
    after = (int(img2.shape[1]), int(img2.shape[0]))
    return frame.with_image(img2, crop_xyxy_norm=xyxy_t, size_before=before, size_after=after)
