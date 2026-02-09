# tests/test_validation_time.py
from __future__ import annotations

from datetime import datetime, timezone, time as dtime

import pytest

from helpers.validation.time import (
    parse_time_of_day,
    dt,
    resolve_time_like,
    ensure_end_after_start,
)
from helpers.validation.basic import ValidationError


def test_parse_time_of_day():
    assert parse_time_of_day("00:00") == dtime(0, 0, 0)
    assert parse_time_of_day("23:59:59") == dtime(23, 59, 59)
    with pytest.raises(ValidationError):
        parse_time_of_day("24:00")
    with pytest.raises(ValidationError):
        parse_time_of_day("nope")


def test_dt_normalizes():
    tz = timezone.utc
    d = datetime(2020, 1, 1, 12, 0, 0)  # naive
    out = dt(d, tz=tz)
    assert out is not None
    assert out.tzinfo == tz

    ts = 0.0
    out2 = dt(ts, tz=tz)
    assert out2 is not None
    assert out2.tzinfo == tz


def test_resolve_time_like_time_of_day_reference():
    tz = timezone.utc
    ref = datetime(2020, 1, 2, 10, 0, 0, tzinfo=tz)
    out = resolve_time_like("23:30", tz=tz, reference=ref)
    assert out.year == 2020 and out.month == 1 and out.day == 2
    assert out.hour == 23 and out.minute == 30


def test_ensure_end_after_start_midnight_guard():
    tz = timezone.utc
    start = datetime(2020, 1, 1, 23, 30, tzinfo=tz)
    end = datetime(2020, 1, 1, 0, 15, tzinfo=tz)  # earlier same day
    out = ensure_end_after_start(start, end)
    assert out.day == 2
    assert out.hour == 0 and out.minute == 15
