# tests/test_strip_map_and_preview.py
from __future__ import annotations

from datetime import timedelta, timezone
import time as _time

import pytest

from helpers.strip_map import (
    FixedStrip,
    TimeSegment,
    progress_to_index,
    segments_to_ranges,
    active_segment_index,
    segment_progress,
    session_playhead_index,
)
from helpers.strip_preview_ascii import (
    preview_ranges_ascii,
    preview_playhead_ascii,
    preview_ranges_with_labels,
    preview_three_bands_ascii,
)
from helpers.time_utils import TimedSession


def test_fixed_strip_clamp_index():
    s = FixedStrip(length=10)
    assert s.clamp_index(-1) == 0
    assert s.clamp_index(0) == 0
    assert s.clamp_index(9) == 9
    assert s.clamp_index(999) == 9

    s2 = FixedStrip(length=0)
    assert s2.clamp_index(999) == 0


def test_progress_to_index_edges():
    strip = FixedStrip(length=10)
    assert progress_to_index(0.0, strip) == 0
    assert progress_to_index(1.0, strip) == 9
    assert progress_to_index(0.999, strip) in range(0, 10)


def test_segments_to_ranges_properties():
    strip = FixedStrip(length=10)
    segs = [
        TimeSegment("a", timedelta(seconds=5)),
        TimeSegment("b", timedelta(seconds=5)),
    ]
    ranges = segments_to_ranges(segs, strip, total_duration=timedelta(seconds=10))
    assert ranges[0][0] == 0
    assert ranges[-1][1] == strip.length
    # monotonic + non-overlapping
    for i in range(1, len(ranges)):
        assert ranges[i][0] >= ranges[i - 1][1]


def test_segments_to_ranges_empty_segments():
    strip = FixedStrip(length=10)
    ranges = segments_to_ranges([], strip, total_duration=timedelta(seconds=10))
    assert ranges == [(0, 10)]


def test_active_segment_index_and_progress():
    tz = timezone.utc
    session = TimedSession()
    session.window.tz = tz
    session.start()

    segs = [
        TimeSegment("a", timedelta(seconds=0.05)),
        TimeSegment("b", timedelta(seconds=0.05)),
    ]
    _time.sleep(0.02)
    idx = active_segment_index(session, segs)
    assert idx in (0, 1)

    p = segment_progress(session, segs)
    assert p is None or (0.0 <= p <= 1.0)


def test_session_playhead_index():
    tz = timezone.utc
    session = TimedSession()
    session.window.tz = tz
    session.start()

    strip = FixedStrip(length=20)
    total = timedelta(seconds=0.2)
    _time.sleep(0.02)
    i = session_playhead_index(session, strip, total_duration=total)
    assert i is None or (0 <= i < strip.length)


def test_preview_ascii_rendering():
    strip = FixedStrip(length=10)
    ranges = [(0, 3), (3, 7), (7, 10)]
    line = preview_ranges_ascii(strip, ranges)
    assert len(line) == 10
    assert line.count(".") == 0

    line2 = preview_playhead_ascii(strip, line, 5, marker="|")
    assert line2[5] == "|"

    multi = preview_ranges_with_labels(strip, ranges, ["a", "b", "c"])
    assert "\n" in multi
    assert multi.splitlines()[0] == line

    three = preview_three_bands_ascii(9)
    assert len(three) == 9
