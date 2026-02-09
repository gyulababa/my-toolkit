# helpers/vision/transforms/colors.py
# Frame-level color/format transforms (thin wrappers over helpers.transforms.imaging).

from __future__ import annotations

from helpers.transforms.imaging import ensure_rgb8_np

from ..frame import Frame, PixelFormat


def ensure_rgb8(frame: Frame) -> Frame:
    """
    Ensure a Frame is RGB8 u8.

    Policy:
      - If frame.fmt indicates BGR/GRAY, convert accordingly.
      - Otherwise "auto" (cannot reliably infer BGR vs RGB from pixels).
    """
    src = "auto"
    if frame.fmt == PixelFormat.BGR8:
        src = "bgr8"
    elif frame.fmt == PixelFormat.GRAY8:
        src = "gray8"
    elif frame.fmt == PixelFormat.RGB8:
        src = "rgb8"

    img2, _ = ensure_rgb8_np(frame.image, src_fmt=src)  # returns rgb8
    return frame.with_image(
        img2,
        fmt=PixelFormat.RGB8,
        src_fmt=src,
        dst_fmt=PixelFormat.RGB8.value,
    )
