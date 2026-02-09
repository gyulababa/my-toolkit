# tests/test_time_utils.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import time as _time

import pytest

from helpers.time_utils import (
    monotonic_s,
    to_unix_seconds,
    delta,
    format_timedelta,
    progress_ratio,
    TimeWindow,
    PauseState,
    TimedSession,
)


def test_monotonic_increases():
    a = monotonic_s()
    _time.sleep(0.01)
    b = monotonic_s()
    assert b >= a


def test_to_unix_seconds_tz_aware():
    tz = timezone.utc
    d = datetime(1970, 1, 1, 0, 0, 0, tzinfo=tz)
    assert to_unix_seconds(d) == 0.0


def test_delta_mixed_inputs():
    tz = timezone.utc
    a = datetime(2020, 1, 1, 0, 0, 0, tzinfo=tz)
    b = datetime(2020, 1, 1, 0, 0, 10, tzinfo=tz)
    assert delta(a, b, tz=tz).total_seconds() == 10

    # unix timestamps
    assert delta(0.0, 10.0, tz=tz).total_seconds() == 10


def test_format_timedelta():
    assert format_timedelta(timedelta(seconds=0)) == "00:00"
    assert format_timedelta(timedelta(seconds=61)) == "01:01"
    assert format_timedelta(timedelta(seconds=3661), show_hours=True) == "01:01:01"
    # negative clamped to 0
    assert format_timedelta(timedelta(seconds=-5)) == "00:00"


def test_progress_ratio():
    assert progress_ratio(timedelta(seconds=0), timedelta(seconds=10)) == 0.0
    assert progress_ratio(timedelta(seconds=10), timedelta(seconds=10)) == 1.0
    assert 0.39 < progress_ratio(timedelta(seconds=4), timedelta(seconds=10)) < 0.41
    assert progress_ratio(timedelta(seconds=10), timedelta(seconds=0)) == 0.0


def test_timewindow_midnight_guard():
    tz = timezone.utc
    w = TimeWindow(tz=tz)
    w.set_start("23:30")
    w.set_end("00:15")
    assert w.start is not None and w.end is not None
    assert w.end > w.start
    assert w.duration() == timedelta(minutes=45)


def test_pause_state_basic():
    tz = timezone.utc
    p = PauseState(tz=tz)
    assert p.is_paused() is False
    p.pause()
    assert p.is_paused() is True
    _time.sleep(0.01)
    p.resume()
    assert p.is_paused() is False
    assert p.paused_duration().total_seconds() > 0.0


def test_timed_session_active_elapsed_paused():
    tz = timezone.utc
    s = TimedSession()
    s.window.tz = tz
    s.start()
    _time.sleep(0.01)
    e1 = s.active_elapsed()
    assert e1 is not None and e1.total_seconds() > 0.0

    s.pause.pause()
    _time.sleep(0.01)
    e2 = s.active_elapsed()
    # while paused, active_elapsed should not advance materially
    assert e2 is not None
    assert (e2 - e1).total_seconds() < 0.02
    s.pause.resume()
