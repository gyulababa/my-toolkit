# helpers/validation/time.py
# Time-related parsing/validation ("input hygiene"): time-of-day parsing, datetime normalization, and duration parsing.

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone, time as dtime
from typing import Optional, Union

from .errors import ValidationError

# datetime or unix seconds
TimeLike = Union[datetime, float, int]

# time-of-day inputs (no date)
TimeOfDayLike = Union[dtime, str]  # "HH:MM" or "HH:MM:SS"


def ensure_tz(t: datetime, tz: timezone = timezone.utc) -> datetime:
    """
    If datetime is naive, attach tz; otherwise keep existing tz.

    Note:
      - We do not convert between timezones here; we only ensure tz-awareness.
    """
    return t.replace(tzinfo=tz) if t.tzinfo is None else t


def parse_time_of_day(s: str) -> dtime:
    """
    Parse "HH:MM" or "HH:MM:SS" into datetime.time.

    Raises:
      ValidationError on invalid formats or ranges.
    """
    raw = s.strip()
    if not re.fullmatch(r"\d{2}:\d{2}(:\d{2})?", raw):
        raise ValidationError(
            f"Invalid time-of-day format: {s!r} (expected 'HH:MM' or 'HH:MM:SS')"
        )

    parts = raw.split(":")
    if len(parts) not in (2, 3):
        raise ValidationError(
            f"Invalid time-of-day format: {s!r} (expected 'HH:MM' or 'HH:MM:SS')"
        )

    try:
        hh = int(parts[0])
        mm = int(parts[1])
        ss = int(parts[2]) if len(parts) == 3 else 0
    except Exception as e:
        raise ValidationError(f"Invalid time-of-day numeric values: {s!r}") from e

    if not (0 <= hh <= 23 and 0 <= mm <= 59 and 0 <= ss <= 59):
        raise ValidationError(f"Invalid time-of-day values: {s!r}")

    return dtime(hour=hh, minute=mm, second=ss)


def dt(value: Union[TimeLike, None], *, tz: timezone = timezone.utc) -> Optional[datetime]:
    """
    Normalize time input to timezone-aware datetime.

    Accepts:
      - datetime → returned (timezone-normalized if naive)
      - float/int → UNIX timestamp seconds
      - None → None
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return ensure_tz(value, tz=tz)
    if isinstance(value, (float, int)):
        return datetime.fromtimestamp(float(value), tz=tz)
    raise TypeError(f"Unsupported time value: {type(value)}")


def resolve_time_like(
    value: Union[TimeLike, TimeOfDayLike, None],
    *,
    tz: timezone,
    reference: Optional[datetime] = None,
) -> Optional[datetime]:
    """
    Resolve either:
      - full datetime / unix seconds (TimeLike)
      - time-of-day (datetime.time or "HH:MM[:SS]") using a reference date

    Midnight-guard is NOT applied here; this function only resolves to a datetime.
    Call ensure_end_after_start() if you need a guard.

    Reference handling:
      - If value is time-of-day and reference is None, we use "today" in tz.
    """
    if value is None:
        return None

    if isinstance(value, (datetime, float, int)):
        return dt(value, tz=tz)

    ref = ensure_tz(reference, tz=tz) if reference is not None else datetime.now(tz)

    if isinstance(value, dtime):
        return datetime(
            year=ref.year,
            month=ref.month,
            day=ref.day,
            hour=value.hour,
            minute=value.minute,
            second=value.second,
            tzinfo=ref.tzinfo,
        )

    if isinstance(value, str):
        tod = parse_time_of_day(value)
        return datetime(
            year=ref.year,
            month=ref.month,
            day=ref.day,
            hour=tod.hour,
            minute=tod.minute,
            second=tod.second,
            tzinfo=ref.tzinfo,
        )

    raise TypeError(f"Unsupported time value: {type(value)}")


def ensure_end_after_start(start: datetime, end: datetime) -> datetime:
    """
    Midnight guard:
    If end < start, assume end is on the next day and add 1 day.

    Specifically meant for time-of-day scheduling:
      start="23:30", end="00:15" -> end becomes next-day 00:15
    """
    if end < start:
        return end + timedelta(days=1)
    return end


_DURATION_TOKEN_RE = re.compile(r"(\d+(?:\.\d+)?)([smhdw])", flags=re.IGNORECASE)


def parse_duration(s: str) -> timedelta:
    """
    Parse a human-friendly duration string into timedelta.

    Supported units:
      s (seconds), m (minutes), h (hours), d (days), w (weeks)

    Examples:
      "90m"     -> 1:30:00
      "1h30m"   -> 1:30:00
      "45s"     -> 0:00:45
      "2d"      -> 2 days
      "1.5h"    -> 1:30:00

    Raises:
      ValidationError for invalid formats.
    """
    raw = s.strip()
    if not raw:
        raise ValidationError("Duration must be a non-empty string")

    matches = list(_DURATION_TOKEN_RE.findall(raw))
    if not matches:
        raise ValidationError(f"Invalid duration format: {s!r} (expected e.g. '1h30m', '90m')")

    total_seconds = 0.0
    consumed = "".join(f"{n}{u}" for n, u in matches)
    if consumed.lower() != raw.lower().replace(" ", ""):
        # Reject unknown characters/tokens.
        raise ValidationError(f"Invalid duration format: {s!r}")

    for num_s, unit in matches:
        n = float(num_s)
        u = unit.lower()
        if u == "s":
            total_seconds += n
        elif u == "m":
            total_seconds += n * 60.0
        elif u == "h":
            total_seconds += n * 3600.0
        elif u == "d":
            total_seconds += n * 86400.0
        elif u == "w":
            total_seconds += n * 604800.0
        else:
            raise ValidationError(f"Unsupported duration unit: {unit!r}")

    return timedelta(seconds=total_seconds)
