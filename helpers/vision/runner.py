# helpers/vision/runner.py
# Background runner that opens a FrameSource, pulls frames on a worker thread, applies transforms, and publishes to a LatestFrameBuffer.

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Callable, List, Optional

from helpers.threading import RateLimiter

from .buffer import LatestFrameBuffer
from .frame import Frame
from .source import FrameSource, SourceInfo

Transform = Callable[[Frame], Frame]


@dataclass
class RunnerStats:
    """
    Lightweight runner statistics.

    Fields:
      running:
        True while the worker thread is considered active.
      frames_in / frames_out:
        Number of frames successfully read / published.
      last_error:
        repr() of the last exception observed in the loop (for UI/log display).
      last_frame_ts:
        The last Frame.ts_monotonic observed (monotonic seconds), if any.
      started_ts:
        Runner start time (time.perf_counter()).
    """
    running: bool = False
    frames_in: int = 0
    frames_out: int = 0
    last_error: Optional[str] = None
    last_frame_ts: Optional[float] = None
    started_ts: Optional[float] = None


class SourceRunner:
    """
    Runs a FrameSource on a background thread and publishes frames into a LatestFrameBuffer.

    Design notes:
      - IMPORTANT: source.open() and source.close() are executed on the worker thread.
        This avoids thread-local issues in some drivers (notably mss on Windows).
      - stop() signals the thread and joins it; close() happens in the worker thread via finally.
    """

    def __init__(
        self,
        source: FrameSource,
        out: LatestFrameBuffer,
        *,
        target_fps: Optional[float] = None,
        transforms: Optional[List[Transform]] = None,
        name: str = "SourceRunner",
    ) -> None:
        self._source = source
        self._out = out
        self._limiter = RateLimiter(target_fps=target_fps)
        self._transforms = transforms or []
        self._name = name

        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

        # Stats are mutated by the worker thread; UI reads best-effort.
        self.stats = RunnerStats()

    def info(self) -> SourceInfo:
        """Return best-effort source metadata from the driver."""
        return self._source.info()

    def start(self) -> None:
        """
        Start the runner thread (idempotent).

        Notes:
          - If already running, no-op.
          - The worker thread will call source.open() before entering the loop.
        """
        if self._thread and self._thread.is_alive():
            return

        self._stop.clear()
        self.stats = RunnerStats(running=True, started_ts=time.perf_counter())

        self._thread = threading.Thread(target=self._loop, name=self._name, daemon=True)
        self._thread.start()

    def stop(self, *, join_timeout_s: float = 2.0) -> None:
        """
        Request stop and join the worker thread.

        Driver requirement:
          - FrameSource.read() should not block indefinitely; otherwise join may time out.
        """
        self._stop.set()

        t = self._thread
        if t:
            t.join(timeout=join_timeout_s)

        # Mark not running (worker thread also flips this on exit).
        self.stats.running = False

    def _apply_transforms(self, frame: Frame) -> Frame:
        """
        Apply transform chain in order.

        If a transform raises, re-raise with contextual info (index + name/repr)
        so the caller can surface a meaningful error.
        """
        out = frame
        for i, t in enumerate(self._transforms):
            try:
                out = t(out)
            except Exception as e:
                tname = getattr(t, "__name__", repr(t))
                raise RuntimeError(f"Transform failed at index {i}: {tname}") from e
        return out

    def _loop(self) -> None:
        """
        Worker thread entry point.

        Lifecycle:
          - open source (worker thread)
          - loop: rate limit -> read -> transform -> publish
          - close source (worker thread, finally)
        """
        try:
            try:
                self._source.open()
            except Exception as e:
                # If open fails, record and exit.
                self.stats.last_error = repr(e)
                return

            while not self._stop.is_set():
                try:
                    self._limiter.sleep_if_needed()

                    frame = self._source.read()
                    if frame is None:
                        continue

                    self.stats.frames_in += 1
                    self.stats.last_frame_ts = frame.ts_monotonic

                    out = self._apply_transforms(frame)
                    self._out.put(out)
                    self.stats.frames_out += 1

                except Exception as e:
                    # Record last error and avoid tight error loops.
                    self.stats.last_error = repr(e)
                    time.sleep(0.1)

        finally:
            try:
                self._source.close()
            except Exception as e:
                # Don't crash the thread on close errors; record for visibility.
                self.stats.last_error = repr(e)
            self.stats.running = False
