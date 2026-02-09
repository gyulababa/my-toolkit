# helpers/vision/frame.py
# Canonical Frame container for vision pipelines (numpy u8 + pixel format + metadata).

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Tuple

import numpy as np


class PixelFormat(str, Enum):
    """
    Canonical internal contract:
      - Frame.image is numpy ndarray, dtype=uint8
      - Default: RGB8 shape (H, W, 3)
    """
    RGB8 = "rgb8"
    BGR8 = "bgr8"
    GRAY8 = "gray8"


@dataclass(frozen=True)
class Frame:
    """
    A single video/capture frame.

    Fields:
      image:
        numpy.ndarray, dtype uint8.
        Canonical: RGB8 (H, W, 3)
      ts_monotonic:
        time.perf_counter() seconds (monotonic) - preferred for timing & rate limiting
      fmt:
        PixelFormat of `image`
      meta:
        arbitrary metadata (device info, monitor index, negotiated FPS, crop/resize info, etc.)
    """
    image: np.ndarray
    ts_monotonic: float
    fmt: PixelFormat = PixelFormat.RGB8
    meta: Dict[str, Any] = field(default_factory=dict)

    @property
    def h(self) -> int:
        """Image height in pixels."""
        return int(self.image.shape[0])

    @property
    def w(self) -> int:
        """Image width in pixels."""
        return int(self.image.shape[1])

    @property
    def c(self) -> Optional[int]:
        """Number of channels if image is HWC; otherwise None."""
        if self.image.ndim == 3:
            return int(self.image.shape[2])
        return None

    @property
    def shape_hwc(self) -> Tuple[int, int, Optional[int]]:
        """Convenience shape tuple (h, w, c)."""
        return (self.h, self.w, self.c)

    def with_image(self, image: np.ndarray, *, fmt: Optional[PixelFormat] = None, **meta_updates: Any) -> "Frame":
        """
        Return a new Frame with updated image, optional format, and merged metadata updates.

        This is the standard transform pattern: do not mutate Frame.meta in-place.
        """
        m = dict(self.meta)
        m.update(meta_updates)
        return Frame(
            image=image,
            ts_monotonic=self.ts_monotonic,
            fmt=fmt or self.fmt,
            meta=m,
        )
