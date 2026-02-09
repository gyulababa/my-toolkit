# helpers/vision/buffer.py
# Thread-safe "latest frame" buffer for producer/consumer pipelines.

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Optional

from .frame import Frame


@dataclass
class LatestFrameBuffer:
    """
    Thread-safe "latest frame" buffer.

    Behavior:
      - put() overwrites the previous frame (only the latest is retained)
      - get_latest() returns immediately (may be None if nothing has been published)
      - wait_next(last_seq) blocks until a new frame is published or timeout

    This is intentionally minimal; it is a synchronization primitive, not a queue.
    """
    _cond: threading.Condition = field(default_factory=lambda: threading.Condition(threading.Lock()))
    _latest: Optional[Frame] = None
    _seq: int = 0

    def put(self, frame: Frame) -> None:
        """Publish a new frame and notify waiters."""
        with self._cond:
            self._latest = frame
            self._seq += 1
            self._cond.notify_all()

    def get_latest(self) -> Optional[Frame]:
        """Return the latest frame (or None if no frame has been published)."""
        with self._cond:
            return self._latest

    def wait_next(self, last_seq: int, *, timeout_s: Optional[float] = None) -> tuple[int, Optional[Frame]]:
        """
        Wait until the internal sequence changes from last_seq, then return (new_seq, frame).

        If timeout expires, returns the current (seq, latest) which may be unchanged.
        """
        with self._cond:
            if self._seq == last_seq:
                self._cond.wait(timeout=timeout_s)
            return self._seq, self._latest

    def seq(self) -> int:
        """Return current publish sequence number."""
        with self._cond:
            return self._seq

    def clear(self) -> None:
        """Drop the latest frame (does not reset seq)."""
        with self._cond:
            self._latest = None
