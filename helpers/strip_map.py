# helpers/strip_map.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import List, Optional, Sequence, Tuple

from .math.basic import clamp, clamp01
from .time_utils import TimedSession, progress_ratio


# -----------------------------------------------------------------------------
# Core strip abstractions
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class FixedStrip:
    """
    Fixed-length discrete axis (e.g. LED strip, timeline slots, frame indices).

    Notes:
    - `length` is a count of discrete positions.
    - Valid indices are [0 .. length-1].
    """
    length: int

    def clamp_index(self, i: int) -> int:
        """
        Clamp an index into [0 .. length-1].

        For length <= 0, returns 0 (defensive default).
        """
        if self.length <= 0:
            return 0
        return int(clamp(int(i), 0, self.length - 1))


# Compatibility alias for future renames.
DiscreteAxis = FixedStrip


# -----------------------------------------------------------------------------
# Progress -> index mapping
# -----------------------------------------------------------------------------

def progress_to_index(progress: float, strip: FixedStrip) -> int:
    """
    Map progress in [0.0, 1.0] to an index on a discrete axis [0, length-1].

    Deterministic, no overflow:
      - progress==0.0 -> 0
      - progress==1.0 -> length-1
    """
    if strip.length <= 0:
        raise ValueError("Strip length must be > 0")

    p = clamp01(progress)
    i = int(p * strip.length)

    # progress == 1.0 must map to last index
    if i >= strip.length:
        return strip.length - 1
    return i


def session_playhead_index(
    session: TimedSession,
    strip: FixedStrip,
    total_duration: timedelta,
) -> Optional[int]:
    """
    Compute playhead position from a TimedSession.

    Returns None if the session has not started.
    """
    elapsed = session.active_elapsed()
    if elapsed is None:
        return None
    p = progress_ratio(elapsed, total_duration)
    return progress_to_index(p, strip)


# -----------------------------------------------------------------------------
# Segment -> contiguous ranges mapping
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class TimeSegment:
    """
    A named time segment.

    Duration is a timedelta to allow callers to stay in datetime/timedelta land.
    """
    name: str
    duration: timedelta


def segments_to_ranges(
    segments: Sequence[TimeSegment],
    strip: FixedStrip,
    total_duration: timedelta,
) -> List[Tuple[int, int]]:
    """
    Map segments to contiguous discrete-axis index ranges [start, end).

    Guarantees:
      - last end == strip.length
      - ranges are monotonic and non-overlapping

    Rationale:
    - Each boundary uses integer flooring, which can introduce rounding artifacts.
      We normalize afterwards to ensure monotonic coverage and to avoid overlaps.
    """
    if strip.length <= 0:
        raise ValueError("Strip length must be > 0")

    total_s = total_duration.total_seconds()
    if total_s <= 0:
        raise ValueError("total_duration must be > 0")

    if not segments:
        # If no segments are provided, treat the entire strip as one range.
        return [(0, strip.length)]

    ranges: List[Tuple[int, int]] = []
    t0 = 0.0

    for idx, seg in enumerate(segments):
        dur = seg.duration.total_seconds()
        if dur < 0:
            raise ValueError(f"Segment '{seg.name}' has negative duration")

        t1 = t0 + dur
        start = int((t0 / total_s) * strip.length)
        end = int((t1 / total_s) * strip.length)

        # Force final boundary to close the strip exactly
        if idx == len(segments) - 1:
            end = strip.length

        ranges.append((start, end))
        t0 = t1

    # Normalize for rounding artifacts (monotonicity, no overlaps)
    fixed: List[Tuple[int, int]] = []
    cur = 0
    for s, e in ranges:
        s = max(s, cur)
        e = max(e, s)
        fixed.append((s, e))
        cur = e

    fixed[0] = (0, fixed[0][1])
    fixed[-1] = (fixed[-1][0], strip.length)
    return fixed


# -----------------------------------------------------------------------------
# Session -> active segment helpers
# -----------------------------------------------------------------------------

def active_segment_index(
    session: TimedSession,
    segments: Sequence[TimeSegment],
) -> Optional[int]:
    """
    Return the active segment index based on elapsed session time.

    Returns None if:
      - session not started, or
      - segments is empty
    """
    elapsed = session.active_elapsed()
    if elapsed is None or not segments:
        return None

    t = elapsed.total_seconds()
    acc = 0.0
    for i, seg in enumerate(segments):
        acc += seg.duration.total_seconds()
        if t < acc:
            return i
    return len(segments) - 1


def segment_progress(
    session: TimedSession,
    segments: Sequence[TimeSegment],
) -> Optional[float]:
    """
    Return progress within the current segment in [0..1].

    Notes:
    - Zero/negative durations are skipped in-progress; they effectively
      collapse to instantaneous segments.
    """
    elapsed = session.active_elapsed()
    if elapsed is None or not segments:
        return None

    t = elapsed.total_seconds()
    acc = 0.0
    for seg in segments:
        dur = seg.duration.total_seconds()
        if dur <= 0:
            continue
        if t < acc + dur:
            return (t - acc) / dur
        acc += dur
    return 1.0
