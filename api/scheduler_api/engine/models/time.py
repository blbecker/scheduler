"""Time primitives.

Every engine time value is a timezone-aware ``datetime`` naming a real instant.
Intervals are half-open — ``[start, end)`` — and all measures are integer
minutes. Never represent time as a slot index or a float.
"""

from __future__ import annotations

from datetime import date, datetime, time as dt_time, timedelta, timezone, tzinfo
from pydantic import BaseModel, ConfigDict, model_validator

#: An interval expressed as ``(start, end)``, half-open.
Interval = tuple[datetime, datetime]


def ensure_aware(value: datetime, field: str) -> None:
    """Raise if ``value`` is naive."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must be timezone-aware")


def ensure_minute_aligned(value: datetime, field: str) -> None:
    """Raise if ``value`` is not aligned to a whole minute."""
    if value.second != 0 or value.microsecond != 0:
        raise ValueError(f"{field} must be aligned to a whole minute")


def to_utc(value: datetime) -> datetime:
    """Return ``value`` as an absolute instant in UTC.

    All interval arithmetic happens in UTC. Adding a ``timedelta`` to an aware
    datetime is wall-clock arithmetic, which silently produces wrong instants
    around daylight-saving transitions.
    """
    return value.astimezone(timezone.utc)


def minutes_between(start: datetime, end: datetime) -> int:
    """Whole minutes between two instants."""
    return int((to_utc(end) - to_utc(start)).total_seconds() // 60)


def local_date(value: datetime, tz: tzinfo) -> date:
    """The local calendar date of an instant."""
    return value.astimezone(tz).date()


def local_midnight_after(value: datetime, tz: tzinfo) -> datetime:
    """The instant of the next local midnight strictly after ``value``'s date."""
    current = value.astimezone(tz)
    next_day = current.date() + timedelta(days=1)
    return datetime.combine(next_day, dt_time.min, tzinfo=tz)


def snap_to_grid(
    value: datetime, granularity_minutes: int, *, direction: str
) -> datetime:
    """Snap ``value`` to a ``granularity_minutes`` boundary in its own timezone.

    ``direction`` is ``"down"`` or ``"up"``. Snapping is wall-clock work on local
    time (that is what makes a schedule legible), so it is done on the local
    representation and converted back to an absolute instant.
    """
    if granularity_minutes <= 0:
        raise ValueError("granularity_minutes must be positive")
    if direction not in {"down", "up"}:
        raise ValueError("direction must be 'down' or 'up'")
    local = value
    minutes_since_midnight = local.hour * 60 + local.minute
    remainder = minutes_since_midnight % granularity_minutes
    if remainder == 0:
        return value
    delta = remainder if direction == "down" else granularity_minutes - remainder
    return (
        value - timedelta(minutes=delta)
        if direction == "down"
        else value + timedelta(minutes=delta)
    )


def is_on_grid(value: datetime, granularity_minutes: int) -> bool:
    """True when ``value`` sits on a ``granularity_minutes`` boundary."""
    if granularity_minutes <= 0:
        raise ValueError("granularity_minutes must be positive")
    return (
        value.hour * 60 + value.minute
    ) % granularity_minutes == 0 and value.second == 0


class TimeWindow(BaseModel):
    """A half-open interval with validated, minute-aligned endpoints."""

    model_config = ConfigDict(frozen=True)

    start: datetime
    end: datetime

    @model_validator(mode="after")
    def _validate(self) -> "TimeWindow":
        ensure_aware(self.start, "start")
        ensure_aware(self.end, "end")
        ensure_minute_aligned(self.start, "start")
        ensure_minute_aligned(self.end, "end")
        if self.end <= self.start:
            raise ValueError("window end must be strictly after start")
        return self

    @property
    def minutes(self) -> int:
        return minutes_between(self.start, self.end)

    @property
    def interval(self) -> Interval:
        return (self.start, self.end)
