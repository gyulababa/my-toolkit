# tests/validation/test_time.py
# Tests for helpers.validation.time utilities (parse_time_of_day, resolve_time_like, midnight guard, parse_duration).

from __future__ import annotations

from datetime import datetime, timezone, time as dtime, timedelta

import pytest

from helpers.validation.time import (
    dt,
    ensure_end_after_start,
    parse_duration,
    parse_time_of_day,
    resolve_time_like,
)


def test_parse_time_of_day_ok() -> None:
    """parse_time_of_day should accept HH:MM and HH:MM:SS."""
    t1 = parse_time_of_day("09:30")
    assert t1 == dtime(hour=9, minute=30, second=0)

    t2 = parse_time_of_day("23:59:58")
    assert t2 == dtime(hour=23, minute=59, second=58)


def test_parse_time_of_day_rejects_bad() -> None:
    """parse_time_of_day should reject invalid formats/ranges."""
    with pytest.raises(Exception):
        parse_time_of_day("9:3")
    with pytest.raises(Exception):
        parse_time_of_day("25:00")
    with pytest.raises(Exception):
        parse_time_of_day("10:60")


def test_dt_normalizes_unix_timestamp() -> None:
    """dt() should accept unix timestamps (seconds) and return tz-aware datetime."""
    out = dt(0, tz=timezone.utc)
    assert out is not None
    assert out.tzinfo is not None


def test_resolve_time_like_time_of_day() -> None:
    """resolve_time_like should resolve time-of-day strings against a reference date."""
    ref = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    out = resolve_time_like("23:30", tz=timezone.utc, reference=ref)
    assert out == datetime(2026, 1, 1, 23, 30, tzinfo=timezone.utc)


def test_midnight_guard_end_after_start() -> None:
    """ensure_end_after_start should add one day when end < start."""
    start = datetime(2026, 1, 1, 23, 30, tzinfo=timezone.utc)
    end = datetime(2026, 1, 1, 0, 15, tzinfo=timezone.utc)
    fixed = ensure_end_after_start(start, end)
    assert fixed == datetime(2026, 1, 2, 0, 15, tzinfo=timezone.utc)


def test_parse_duration() -> None:
    """parse_duration should support s/m/h/d/w and compound forms."""
    assert parse_duration("90m") == timedelta(minutes=90)
    assert parse_duration("1h30m") == timedelta(minutes=90)
    assert parse_duration("45s") == timedelta(seconds=45)
    assert parse_duration("1.5h") == timedelta(minutes=90)

    with pytest.raises(Exception):
        parse_duration("")
    with pytest.raises(Exception):
        parse_duration("abc")
    with pytest.raises(Exception):
        parse_duration("1x")
