# helpers/vision/drivers/uvc_opencv.py
# UVC (USB camera) driver via OpenCV VideoCapture (optional dependency).
# Produces BGR8 u8 Frames by default (OpenCV native); pipeline can convert to RGB8.

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import numpy as np

from helpers.threading import RateLimiter

from ..frame import Frame, PixelFormat
from ..source import FrameSource, SourceInfo


def _require_cv2():
    """
    Import optional dependency `cv2` with a friendly error.

    We keep this optional because many projects won't need UVC capture.
    """
    try:
        import cv2  # type: ignore
        return cv2
    except Exception as e:
        raise RuntimeError(
            "Missing optional dependency 'opencv-python' (cv2). Install it to use UvcOpenCvSource."
        ) from e


def _fourcc_code(cv2: Any, s: str) -> int:
    """Convert a FourCC string like 'MJPG' to an int code for cv2."""
    s = (s or "").strip()
    if len(s) != 4:
        raise ValueError(f"fourcc must be a 4-char string (got {s!r})")
    return int(cv2.VideoWriter_fourcc(*s))


def _resolve_backend(cv2: Any, backend: Optional[int | str]) -> Optional[int]:
    """
    Resolve backend input to an OpenCV CAP_* constant.

    Supports:
      - None: OpenCV default
      - int: passed through
      - str: one of {"any","dshow","msmf","v4l2","gstreamer"} (case-insensitive)
    """
    if backend is None:
        return None
    if isinstance(backend, int):
        return backend

    key = str(backend).strip().lower()
    if key in ("", "none", "auto", "default"):
        return None
    if key in ("any",):
        return int(getattr(cv2, "CAP_ANY"))
    if key in ("dshow", "directshow"):
        return int(getattr(cv2, "CAP_DSHOW"))
    if key in ("msmf",):
        return int(getattr(cv2, "CAP_MSMF"))
    if key in ("v4l2", "v4l"):
        return int(getattr(cv2, "CAP_V4L2"))
    if key in ("gstreamer", "gst"):
        return int(getattr(cv2, "CAP_GSTREAMER"))

    raise ValueError(f"Unknown OpenCV backend: {backend!r}")


@dataclass
class UvcOpenCvSource(FrameSource):
    """
    UVC camera capture using OpenCV (cv2.VideoCapture).

    Output contract:
      - Frame.image: np.ndarray, dtype=uint8
      - Default Frame.fmt: PixelFormat.BGR8 (OpenCV native)
      - Frame.ts_monotonic: time.perf_counter() seconds

    Parameters:
      device_index:
        OpenCV camera index (0,1,2...)
      width/height:
        Best-effort requested resolution.
      fps:
        Best-effort requested capture FPS.
      fourcc:
        Best-effort requested codec (e.g. "MJPG"). None means "auto".
      buffersize:
        Best-effort capture buffer size. 1 helps with latency on many backends.
      target_fps:
        Optional pacing in the driver (separate from camera fps setting).
      backend:
        Optional OpenCV backend (int CAP_* or str like "dshow"/"msmf"/"any").
        On Windows, "dshow" tends to be most reliable for UVC preview.
    """

    device_index: int = 0
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    fourcc: Optional[str] = None
    buffersize: Optional[int] = 1

    target_fps: Optional[float] = None
    backend: Optional[int | str] = "dshow"

    _cap: Any = field(default=None, init=False, repr=False)
    _limiter: RateLimiter = field(default_factory=lambda: RateLimiter(target_fps=None), init=False, repr=False)
    _negotiated: Dict[str, Any] = field(default_factory=dict, init=False, repr=False)
    _backend_used: Optional[int] = field(default=None, init=False, repr=False)

    def open(self) -> None:
        """Open the camera and attempt best-effort property negotiation (probe-aligned ordering)."""
        cv2 = _require_cv2()

        b = _resolve_backend(cv2, self.backend)
        self._backend_used = b

        # Open capture
        cap = cv2.VideoCapture(self.device_index) if b is None else cv2.VideoCapture(self.device_index, b)
        if not cap or not cap.isOpened():
            raise RuntimeError(
                f"Failed to open camera device_index={self.device_index} backend={self.backend!r} (resolved={b})"
            )

        # Probe-like ordering:
        # 1) buffersize (reduce latency)
        if self.buffersize is not None:
            try:
                cap.set(cv2.CAP_PROP_BUFFERSIZE, float(int(self.buffersize)))
            except Exception:
                pass

        # 2) resolution first
        if self.width is not None:
            try:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(self.width))
            except Exception:
                pass
        if self.height is not None:
            try:
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(self.height))
            except Exception:
                pass

        # 3) fps next
        if self.fps is not None:
            try:
                cap.set(cv2.CAP_PROP_FPS, float(self.fps))
            except Exception:
                pass

        # 4) FOURCC last (often MJPG helps, but allow None/"auto")
        if self.fourcc:
            try:
                cap.set(cv2.CAP_PROP_FOURCC, _fourcc_code(cv2, self.fourcc))
            except Exception:
                pass

        self._cap = cap
        self._limiter = RateLimiter(target_fps=self.target_fps)

        # Read back negotiated properties for info()/meta (best-effort)
        self._negotiated = {}
        try:
            w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            f = cap.get(cv2.CAP_PROP_FPS)
            fourcc_i = cap.get(cv2.CAP_PROP_FOURCC)

            self._negotiated = {
                "width": int(w) if w else None,
                "height": int(h) if h else None,
                "fps": float(f) if f else None,
                "fourcc_int": int(fourcc_i) if fourcc_i else None,
                "buffersize": int(cap.get(cv2.CAP_PROP_BUFFERSIZE) or 0) or None,
            }
        except Exception:
            self._negotiated = {}

        # Quick smoke-test read (fail loud as Python exception instead of "black UI")
        ok, img = cap.read()
        if not ok or img is None:
            raise RuntimeError(
                f"Camera opened but failed to read first frame: device_index={self.device_index} backend={self.backend!r}"
            )

    def close(self) -> None:
        """Release the OpenCV capture handle (best-effort)."""
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
        self._cap = None
        self._limiter.reset()
        self._negotiated = {}
        self._backend_used = None

    def info(self) -> SourceInfo:
        """Return best-effort metadata about the capture device."""
        extra = {
            "device_index": self.device_index,
            "backend": self.backend,
            "backend_used": self._backend_used,
            "fourcc": self.fourcc,
            "requested": {"width": self.width, "height": self.height, "fps": self.fps, "buffersize": self.buffersize},
            "negotiated": dict(self._negotiated),
        }
        return SourceInfo(
            name="uvc_opencv",
            width=self._negotiated.get("width"),
            height=self._negotiated.get("height"),
            fps=self._negotiated.get("fps") or self.fps,
            extra=extra,
        )

    def read(self) -> Optional[Frame]:
        """
        Read one frame.

        Notes:
          - OpenCV returns frames as BGR uint8 by default.
          - We emit BGR8 and let the pipeline normalize to RGB8 via transforms if needed.
        """
        if self._cap is None:
            return None

        self._limiter.sleep_if_needed()

        ok, img = self._cap.read()
        if not ok or img is None:
            return None

        if not isinstance(img, np.ndarray):
            return None
        if img.dtype != np.uint8:
            img = img.astype(np.uint8, copy=False)

        ts = time.perf_counter()
        meta = {
            "driver": "uvc_opencv",
            "device_index": self.device_index,
            "backend_used": self._backend_used,
        }
        return Frame(image=img, ts_monotonic=ts, fmt=PixelFormat.BGR8, meta=meta)
