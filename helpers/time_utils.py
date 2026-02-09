# helpers/time_utils.py
from __future__ import annotations

"""
helpers.time_utils
------------------

Time normalization and calculations, plus small stateful time helpers
(TimeWindow / PauseState / TimedSession).

Key idea:
- This module operates on *already normalized* datetimes and timedeltas.
- Parsing and input validation live in validation_time.py.
"""

import time as _time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional

from .math.basic import clamp01
from .validation.time import (
    TimeLike,
    TimeOfDayLike,
    dt,
    ensure_tz,
    resolve_time_like,
    ensure_end_after_start,
)


def now(tz: timezone = timezone.utc) -> datetime:
    """
    Authoritative current wall-clock time in the given timezone.

    Use this for "real time" events and timestamps.

    If you need stable deltas for animation / loops, prefer monotonic_s().
    """
    return datetime.now(tz=tz)


def utc_now_iso() -> str:
    """
    Return current UTC time as ISO-8601 string with 'Z' suffix.

    Example:
      '2026-01-26T19:10:00Z'

    Notes:
    - microseconds are removed for stable diffs and readability
    - uses timezone-aware UTC
    """
    return now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def monotonic_s() -> float:
    """
    Monotonic time in seconds (never goes backwards).

    Use for:
    - frame deltas
    - animations
    - timers where wall-clock changes should not affect duration
    """
    return _time.monotonic()


def to_unix_seconds(t: datetime) -> float:
    """Convert datetime to unix seconds (ensures tz-awareness first)."""
    return ensure_tz(t).timestamp()


def delta(a: TimeLike, b: TimeLike, *, tz: timezone = timezone.utc) -> timedelta:
    """
    Return (b - a). Works with datetime or unix seconds.

    Note:
    - For float/int inputs, values are treated as UNIX timestamps (seconds).
    """
    da = dt(a, tz=tz)
    db = dt(b, tz=tz)
    return db - da


def since(start: TimeLike, *, tz: timezone = timezone.utc) -> timedelta:
    """Return (now - start)."""
    return delta(start, now(tz), tz=tz)


def until(end: TimeLike, *, tz: timezone = timezone.utc) -> timedelta:
    """Return (end - now)."""
    return delta(now(tz), end, tz=tz)


def safe_total_seconds(td: timedelta) -> float:
    """Small wrapper to keep call sites uniform."""
    return td.total_seconds()


def clamp_timedelta(td: timedelta, *, min_td: timedelta, max_td: timedelta) -> timedelta:
    """Clamp a timedelta to [min_td, max_td]."""
    if td < min_td:
        return min_td
    if td > max_td:
        return max_td
    return td


def floor_to(t: datetime, *, seconds: int) -> datetime:
    """
    Floor datetime to nearest multiple of `seconds` since epoch.

    Useful for tick alignment (e.g., snap to 1s / 5s boundaries).
    """
    if seconds <= 0:
        raise ValueError("seconds must be > 0")
    t = ensure_tz(t)
    epoch = int(t.timestamp())
    floored = (epoch // seconds) * seconds
    return datetime.fromtimestamp(floored, tz=t.tzinfo)


def ceil_to(t: datetime, *, seconds: int) -> datetime:
    """
    Ceil datetime to nearest multiple of `seconds` since epoch.
    """
    if seconds <= 0:
        raise ValueError("seconds must be > 0")
    t = ensure_tz(t)
    epoch = int(t.timestamp())
    ceiled = ((epoch + seconds - 1) // seconds) * seconds
    return datetime.fromtimestamp(ceiled, tz=t.tzinfo)


def format_timedelta(td: timedelta, *, show_hours: bool = False) -> str:
    """
    Format timedelta as mm:ss or hh:mm:ss.

    Behavior:
    - Negative timedeltas are clamped to 0 (display does not show minus).
    """
    total_seconds = int(max(0, td.total_seconds()))
    seconds = total_seconds % 60
    minutes = (total_seconds // 60) % 60
    hours = total_seconds // 3600

    if show_hours or hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def progress_ratio(elapsed: timedelta, total: timedelta) -> float:
    """
    Return progress in [0.0, 1.0].

    - If total <= 0, returns 0.0.
    """
    tot = total.total_seconds()
    if tot <= 0:
        return 0.0
    return clamp01(elapsed.total_seconds() / tot)


@dataclass
class TimeWindow:
    """
    A simple start/end window in a given timezone.

    Supports mixed inputs:
      - full datetimes
      - unix seconds
      - time-of-day (datetime.time or "HH:MM[:SS]")

    Midnight guard:
      - If you set start/end with time-of-day and end < start,
        end is assumed to be on the next day.
    """
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    tz: timezone = timezone.utc

    def set_start(self, t: Optional[TimeLike | TimeOfDayLike] = None) -> None:
        # If caller doesn't provide a time, treat it as "now".
        self.start = now(self.tz) if t is None else resolve_time_like(t, tz=self.tz)

        # If end already exists and is earlier, roll it (midnight guard)
        if self.start and self.end:
            self.end = ensure_end_after_start(self.start, self.end)

    def set_end(self, t: Optional[TimeLike | TimeOfDayLike] = None) -> None:
        # Resolve end relative to start if start exists, else relative to now.
        ref = self.start if self.start is not None else now(self.tz)
        self.end = resolve_time_like(t, tz=self.tz, reference=ref)

        # Midnight guard if start exists
        if self.start and self.end:
            self.end = ensure_end_after_start(self.start, self.end)

    def elapsed(self) -> Optional[timedelta]:
        """Wall-clock elapsed since start (ignores PauseState)."""
        if self.start:
            return now(self.tz) - self.start
        return None

    def remaining(self) -> Optional[timedelta]:
        """Wall-clock remaining until end (ignores PauseState)."""
        if self.end:
            return self.end - now(self.tz)
        return None

    def contains(self, t: Optional[TimeLike | TimeOfDayLike] = None) -> bool:
        """Return True if t (or now) is within [start, end]."""
        cur = resolve_time_like(t, tz=self.tz) if t is not None else now(self.tz)

        if self.start and cur < self.start:
            return False
        if self.end and cur > self.end:
            return False
        return True

    def duration(self) -> Optional[timedelta]:
        """Return (end - start) if both exist."""
        if self.start and self.end:
            return self.end - self.start
        return None


@dataclass
class PauseState:
    """
    Tracks paused duration without stopping wall-clock time.

    This intentionally stores pause/resume instants explicitly:
    - paused_at: when the current pause began (None if not paused)
    - last_paused_at / last_resumed_at: last transition times
    - total_paused: accumulated paused time across pauses
    """
    tz: timezone = timezone.utc
    paused_at: Optional[datetime] = None
    last_paused_at: Optional[datetime] = None
    last_resumed_at: Optional[datetime] = None
    total_paused: timedelta = field(default_factory=timedelta)

    def pause(self) -> None:
        """Begin a pause if not already paused."""
        if self.paused_at is None:
            t = now(self.tz)
            self.paused_at = t
            self.last_paused_at = t

    def resume(self) -> None:
        """End a pause if currently paused; accumulate paused duration."""
        if self.paused_at is not None:
            t = now(self.tz)
            self.total_paused += (t - self.paused_at)
            self.paused_at = None
            self.last_resumed_at = t

    def is_paused(self) -> bool:
        return self.paused_at is not None

    def paused_duration(self) -> timedelta:
        """
        Total paused duration including an active pause (if any).
        """
        if self.paused_at:
            return self.total_paused + (now(self.tz) - self.paused_at)
        return self.total_paused

    def since_last_pause(self) -> Optional[timedelta]:
        """
        Time since last resume.

        Returns None if:
        - never resumed
        - currently paused
        """
        if self.paused_at is not None or self.last_resumed_at is None:
            return None
        return now(self.tz) - self.last_resumed_at

    def last_pause_at(self) -> Optional[datetime]:
        """Datetime when the last pause started."""
        return self.last_paused_at

    def reset(self) -> None:
        """Clear pause history and accumulated paused time."""
        self.paused_at = None
        self.last_paused_at = None
        self.last_resumed_at = None
        self.total_paused = timedelta()


@dataclass
class TimedSession:
    """
    A start/end window with pause awareness.

    active_elapsed() / active_remaining() subtract/add paused duration so the session's
    "active time" does not advance while paused.
    """
    window: TimeWindow = field(default_factory=TimeWindow)
    pause: PauseState = field(default_factory=PauseState)

    def __post_init__(self) -> None:
        # Keep pause tz aligned to window tz
        self.pause.tz = self.window.tz

    def start(self) -> None:
        self.window.set_start()
        self.pause.tz = self.window.tz
        self.pause.reset()

    def end(self) -> None:
        self.window.set_end()

    def active_elapsed(self) -> Optional[timedelta]:
        if not self.window.start:
            return None
        return (now(self.window.tz) - self.window.start) - self.pause.paused_duration()

    def active_remaining(self) -> Optional[timedelta]:
        if not self.window.end:
            return None
        return (self.window.end - now(self.window.tz)) + self.pause.paused_duration()
