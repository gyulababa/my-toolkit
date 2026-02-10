# helpers/toolkits/ui/runtime/autosave.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from helpers.threading.rate_limiter import RateLimiter


@dataclass
class UiStateAutosaver:
    """
    Rate-limited autosaver.
    - Call mark_dirty() when UI state changes.
    - Call pump(save_fn) frequently (e.g., once per frame).
    - save_fn is called only when dirty and the interval elapsed.
    """
    interval_s: float = 2.0
    _dirty: bool = False

    def __post_init__(self) -> None:
        fps = (1.0 / float(self.interval_s)) if self.interval_s > 0 else 0.0
        self._limiter = RateLimiter(target_fps=fps if fps > 0 else None)

    def mark_dirty(self) -> None:
        self._dirty = True

    def pump(self, save_fn: Callable[[], None]) -> None:
        if not self._dirty:
            return
        # Only allow a save at ~1/interval_s cadence.
        self._limiter.sleep_if_needed()
        if not self._dirty:
            return
        save_fn()
        self._dirty = False
