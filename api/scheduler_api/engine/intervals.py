"""Interval arithmetic.

Everything the engine measures is measured here, in integer minutes, using a
sweep over sorted endpoints. Never build per-minute arrays: a 28-day horizon has
40,320 minutes per job, and the sweep is both faster and exact.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone, tzinfo

from scheduler_api.engine.models.time import (
    Interval,
    minutes_between,
    to_utc,
)


@dataclass(frozen=True)
class CoverageMeasurement:
    """Result of comparing demand against assigned staffing."""

    required_minutes: int
    assigned_minutes: int
    covered_minutes: int
    uncovered_minutes: int
    excess_minutes: int

    @property
    def coverage_ratio(self) -> float:
        if self.required_minutes <= 0:
            return 1.0
        return self.covered_minutes / self.required_minutes


def overlaps(
    a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime
) -> bool:
    """True when two half-open intervals overlap. Touching intervals do not."""
    return to_utc(a_start) < to_utc(b_end) and to_utc(b_start) < to_utc(a_end)


def overlap_minutes(
    a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime
) -> int:
    """Minutes shared by two half-open intervals."""
    start = max(to_utc(a_start), to_utc(b_start))
    end = min(to_utc(a_end), to_utc(b_end))
    if end <= start:
        return 0
    return int((end - start).total_seconds() // 60)


def merge_intervals(intervals: list[Interval]) -> list[Interval]:
    """Merge overlapping and touching intervals into a minimal disjoint set."""
    if not intervals:
        return []
    ordered = sorted(
        ((to_utc(start), to_utc(end)) for start, end in intervals), key=lambda i: i[0]
    )
    merged: list[Interval] = [ordered[0]]
    for start, end in ordered[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def minutes_inside(start: datetime, end: datetime, windows: list[Interval]) -> int:
    """Minutes of ``[start, end)`` that fall inside the union of ``windows``."""
    target_start, target_end = to_utc(start), to_utc(end)
    if target_end <= target_start:
        return 0
    return sum(
        overlap_minutes(target_start, target_end, window_start, window_end)
        for window_start, window_end in merge_intervals(windows)
    )


def uncovered_parts(
    start: datetime, end: datetime, windows: list[Interval]
) -> list[Interval]:
    """Parts of ``[start, end)`` that fall outside the union of ``windows``."""
    target_start, target_end = to_utc(start), to_utc(end)
    remainder: list[Interval] = []
    cursor = target_start
    for window_start, window_end in merge_intervals(windows):
        if window_end <= cursor:
            continue
        if window_start >= target_end:
            break
        if window_start > cursor:
            remainder.append((cursor, min(window_start, target_end)))
        cursor = max(cursor, window_end)
        if cursor >= target_end:
            break
    if cursor < target_end:
        remainder.append((cursor, target_end))
    return remainder


def measure_coverage(
    demand: list[tuple[datetime, datetime, int]],
    assigned: list[Interval],
) -> CoverageMeasurement:
    """Sweep demand counts against assigned staffing counts.

    ``demand`` items are ``(start, end, required_workers)``; ``assigned`` items are
    individual staffing intervals that each contribute one worker.
    """
    events: dict[datetime, list[tuple[int, int]]] = defaultdict(list)
    for start, end, count in demand:
        if count <= 0 or to_utc(end) <= to_utc(start):
            continue
        events[to_utc(start)].append((count, 0))
        events[to_utc(end)].append((-count, 0))
    for start, end in assigned:
        if to_utc(end) <= to_utc(start):
            continue
        events[to_utc(start)].append((0, 1))
        events[to_utc(end)].append((0, -1))

    if not events:
        return CoverageMeasurement(0, 0, 0, 0, 0)

    times = sorted(events)
    required = assigned_minutes = covered = uncovered = excess = 0
    demand_count = assigned_count = 0
    for index, moment in enumerate(times):
        for demand_delta, assigned_delta in events[moment]:
            demand_count += demand_delta
            assigned_count += assigned_delta
        if index + 1 >= len(times):
            break
        duration = minutes_between(moment, times[index + 1])
        if duration <= 0:
            continue
        required += demand_count * duration
        assigned_minutes += assigned_count * duration
        covered += min(demand_count, assigned_count) * duration
        if assigned_count > demand_count:
            excess += (assigned_count - demand_count) * duration
        elif demand_count > assigned_count:
            uncovered += (demand_count - assigned_count) * duration
    return CoverageMeasurement(required, assigned_minutes, covered, uncovered, excess)


def minutes_by_local_date(
    start: datetime, end: datetime, tz: tzinfo
) -> dict[date, int]:
    """Split an interval's minutes across the local dates it touches.

    Local days are 23 or 25 hours long across DST transitions, so this walks local
    midnights as absolute instants rather than assuming a fixed day length.
    """
    minutes: dict[date, int] = {}
    cursor = to_utc(start)
    target_end = to_utc(end)
    while cursor < target_end:
        current_date = cursor.astimezone(tz).date()
        next_midnight = datetime.combine(
            current_date + timedelta(days=1), time.min, tzinfo=tz
        ).astimezone(timezone.utc)
        segment_end = min(target_end, next_midnight)
        if segment_end <= cursor:  # defensive: never loop forever at a DST edge
            segment_end = min(target_end, cursor + timedelta(minutes=1))
        minutes[current_date] = minutes.get(current_date, 0) + minutes_between(
            cursor, segment_end
        )
        cursor = segment_end
    return minutes
