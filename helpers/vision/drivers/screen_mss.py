# helpers/vision/drivers/screen_mss.py
# Screen capture driver using mss (optional dependency). Produces RGB8 u8 Frames.

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import numpy as np

from helpers.threading import RateLimiter

from ..frame import Frame, PixelFormat
from ..source import FrameSource, SourceInfo


def _require_mss():
    """
    Import optional dependency `mss` with a friendly error.

    This keeps helpers/vision usable without forcing mss install for all consumers.
    """
    try:
        import mss  # type: ignore
        return mss
    except Exception as e:
        raise RuntimeError("Missing optional dependency 'mss'. Install it to use ScreenMssSource.") from e


@dataclass
class ScreenMssSource(FrameSource):
    """
    Screen capture via `mss`.

    Output contract:
      - Frame.image: np.ndarray, dtype=uint8
      - Frame.fmt: PixelFormat.RGB8
      - Frame.ts_monotonic: time.perf_counter() seconds

    Parameters:
      monitor:
        0 = "all monitors" virtual bbox (mss semantics),
        1..N specific monitor.
      target_fps:
        Optional limiter inside the driver; you can also limit in SourceRunner.
        If both are set, you'll effectively limit twice (usually avoid that).
    """

    monitor: int = 1
    target_fps: Optional[float] = None

    _sct: Any = field(default=None, init=False, repr=False)
    _mon: Optional[Dict[str, int]] = field(default=None, init=False, repr=False)
    _limiter: RateLimiter = field(default_factory=lambda: RateLimiter(target_fps=None), init=False, repr=False)

    def open(self) -> None:
        """
        Open the mss capture context and resolve the monitor bbox.

        Important:
          - mss uses thread-local resources on Windows; `open()` should be called
            in the same thread that will call `read()`.
        """
        self._open_sct()

        # Smoke-test a single grab here so we fail loudly (Python exception)
        # instead of crashing later in the UI loop.
        _ = self._grab_rgb_once()

    def _open_sct(self) -> None:
        """(Re)create the mss instance and monitor rect."""
        mss = _require_mss()
        self._sct = mss.mss()

        try:
            self._mon = self._sct.monitors[self.monitor]
        except Exception as e:
            # Provide a helpful error for invalid monitor indexes.
            try:
                count = len(self._sct.monitors) - 1
            except Exception:
                count = None
            raise RuntimeError(
                f"screen_mss: invalid monitor index {self.monitor}. "
                f"Available monitors: {count if count is not None else 'unknown'}"
            ) from e

        self._limiter = RateLimiter(target_fps=self.target_fps)

    def close(self) -> None:
        """Close the mss context (best-effort)."""
        if self._sct is not None:
            try:
                self._sct.close()
            except Exception:
                pass
        self._sct = None
        self._mon = None
        self._limiter.reset()

    def info(self) -> SourceInfo:
        """Return best-effort metadata about the selected monitor capture."""
        if not self._mon:
            return SourceInfo(name="screen_mss", extra={"monitor": self.monitor})
        return SourceInfo(
            name="screen_mss",
            width=int(self._mon["width"]),
            height=int(self._mon["height"]),
            fps=self.target_fps,
            extra={"monitor": self.monitor, "left": int(self._mon["left"]), "top": int(self._mon["top"])},
        )

    def _grab_rgb_once(self) -> np.ndarray:
        """Grab BGRA once and convert to RGB (uint8)."""
        if self._sct is None or self._mon is None:
            raise RuntimeError("screen_mss: not opened")

        raw = self._sct.grab(self._mon)              # BGRA
        img = np.array(raw, dtype=np.uint8)          # (H, W, 4)
        bgr = img[:, :, :3]                          # (H, W, 3)
        return bgr[:, :, ::-1].copy()                # RGB

    def read(self) -> Optional[Frame]:
        """
        Capture one frame.

        Notes:
          - mss.grab returns BGRA; we convert to RGB8.
          - Conversion makes a copy to ensure a contiguous RGB array.
          - On Windows, mss uses thread-local handle state; if that state is missing
            we recreate the mss instance and retry once.
        """
        if self._sct is None or self._mon is None:
            return None

        self._limiter.sleep_if_needed()

        try:
            rgb = self._grab_rgb_once()
        except AttributeError as e:
            msg = str(e)
            if "_thread._local" in msg and ("srcdc" in msg or "srdc" in msg):
                # Recreate in current thread and retry once.
                try:
                    self.close()
                except Exception:
                    pass
                self._open_sct()
                rgb = self._grab_rgb_once()
            else:
                raise

        ts = time.perf_counter()
        return Frame(image=rgb, ts_monotonic=ts, fmt=PixelFormat.RGB8, meta={"driver": "screen_mss", "monitor": self.monitor})
