# helpers/threading/rate_limiter.py
# Simple, reusable timing helpers for background loops (rate limiting, tick-based pacing).

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class RateLimiter:
    """
    Simple rate limiter based on time.perf_counter().

    Intended use:
      - background loops (frame capture, polling, periodic work)
      - pacing producers to a target FPS / Hz

    Semantics:
      - Uses monotonic clock (perf_counter) to avoid wall-clock jumps.
      - If target_fps is None/0/negative, rate limiting is disabled.
      - After sleeping, internal "last tick" is updated to the post-sleep timestamp.
    """
    target_fps: Optional[float] = None
    _last: Optional[float] = None

    def reset(self) -> None:
        """Reset internal timing state (next tick acts as the first)."""
        self._last = None

    def tick(self) -> None:
        """Alias for sleep_if_needed()."""
        self.sleep_if_needed()

    def sleep_if_needed(self) -> None:
        """
        Sleep long enough so that calls occur at approximately target_fps.

        Typical usage:
          limiter = RateLimiter(target_fps=20)
          while running:
              limiter.sleep_if_needed()
              do_work()
        """
        if not self.target_fps or self.target_fps <= 0:
            return

        now = time.perf_counter()
        if self._last is None:
            self._last = now
            return

        min_dt = 1.0 / float(self.target_fps)
        dt = now - self._last
        if dt >= min_dt:
            # We're already slow enough; just move the anchor forward.
            self._last = now
            return

        sleep_s = max(0.0, min_dt - dt)
        time.sleep(sleep_s)
        # Anchor to "after sleep" so the next tick is spaced correctly.
        self._last = time.perf_counter()
