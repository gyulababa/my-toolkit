# helpers/vision/transforms/resize.py
# Frame-level resize transforms (thin wrappers over helpers.transforms.imaging).

from __future__ import annotations

from typing import Literal

from helpers.transforms.imaging import resize_fit_aspect_np, resize_max_np

from ..frame import Frame


def resize_max(frame: Frame, *, max_w: int, max_h: int) -> Frame:
    """
    Resize to fit within (max_w, max_h), preserving aspect ratio.

    Delegates to helpers.transforms.imaging.resize_max_np.
    Records metadata about the operation on the Frame.
    """
    before = (frame.w, frame.h)
    img2 = resize_max_np(frame.image, max_w=max_w, max_h=max_h)
    after = (int(img2.shape[1]), int(img2.shape[0]))
    return frame.with_image(img2, resized_max=(max_w, max_h), size_before=before, size_after=after)


def resize_fit_aspect(
    frame: Frame,
    *,
    dst_w: int,
    dst_h: int,
    mode: Literal["contain", "cover"] = "contain",
) -> Frame:
    """
    Resize to (dst_w, dst_h) using aspect-fit.

    mode:
      - "contain": letterbox style fit
      - "cover": crop style fit

    Delegates to helpers.transforms.imaging.resize_fit_aspect_np.
    Records metadata about the operation on the Frame.
    """
    before = (frame.w, frame.h)
    img2 = resize_fit_aspect_np(frame.image, dst_w=dst_w, dst_h=dst_h, mode=mode)
    after = (int(img2.shape[1]), int(img2.shape[0]))
    return frame.with_image(img2, resized_fit=(dst_w, dst_h, mode), size_before=before, size_after=after)
