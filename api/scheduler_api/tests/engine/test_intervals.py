"""Interval arithmetic: the foundation everything else measures with."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from scheduler_api.engine.intervals import (
    measure_coverage,
    merge_intervals,
    minutes_by_local_date,
    minutes_inside,
    overlap_minutes,
    overlaps,
    uncovered_parts,
)
from scheduler_api.tests.engine.builders import at

NEW_YORK = ZoneInfo("America/New_York")


def test_touching_intervals_do_not_overlap() -> None:
    assert not overlaps(at(8), at(12), at(12), at(16))
    assert overlaps(at(8), at(12), at(11), at(16))
    assert overlap_minutes(at(8), at(12), at(12), at(16)) == 0
    assert overlap_minutes(at(8), at(12), at(11), at(16)) == 60


def test_merge_intervals_collapses_overlaps_and_touching() -> None:
    merged = merge_intervals(
        [(at(8), at(12)), (at(11), at(14)), (at(14), at(16)), (at(18), at(19))]
    )
    assert merged == [(at(8), at(16)), (at(18), at(19))]


def test_minutes_inside_counts_only_covered_minutes() -> None:
    windows = [(at(8), at(10)), (at(12), at(14))]
    assert minutes_inside(at(8), at(14), windows) == 240
    assert minutes_inside(at(9), at(13), windows) == 120
    assert minutes_inside(at(10), at(12), windows) == 0


def test_uncovered_parts_returns_the_gaps() -> None:
    windows = [(at(8), at(10)), (at(12), at(14))]
    gaps = uncovered_parts(at(9), at(13), windows)
    assert gaps == [(at(10), at(12))]


def test_uncovered_parts_with_no_windows_returns_the_whole_interval() -> None:
    assert uncovered_parts(at(9), at(11), []) == [(at(9), at(11))]


def test_coverage_measurement_counts_covered_uncovered_and_excess() -> None:
    demand = [(at(8), at(12), 2)]  # 240 minutes at headcount 2 = 480 required minutes
    assigned = [(at(8), at(10))]  # one worker for 120 minutes
    measurement = measure_coverage(demand, assigned)
    assert measurement.required_minutes == 480
    assert measurement.assigned_minutes == 120
    assert measurement.covered_minutes == 120
    assert measurement.uncovered_minutes == 360
    assert measurement.excess_minutes == 0
    assert measurement.coverage_ratio == pytest.approx(0.25)


def test_coverage_measurement_reports_excess_staffing() -> None:
    demand = [(at(8), at(12), 1)]
    assigned = [(at(8), at(12)), (at(9), at(11))]
    measurement = measure_coverage(demand, assigned)
    assert measurement.covered_minutes == 240
    assert measurement.excess_minutes == 120
    assert measurement.uncovered_minutes == 0


def test_simultaneous_windows_sum_their_headcount() -> None:
    demand = [(at(8), at(12), 2), (at(10), at(14), 1)]
    measurement = measure_coverage(demand, [])
    # 08-10: 2 * 120 = 240; 10-12: 3 * 120 = 360; 12-14: 1 * 120 = 120
    assert measurement.required_minutes == 720


def test_empty_demand_and_assignment_measure_zero() -> None:
    measurement = measure_coverage([], [])
    assert measurement.required_minutes == 0
    assert measurement.coverage_ratio == 1.0


def test_minutes_by_local_date_splits_a_shift_across_midnight() -> None:
    start = datetime(2026, 11, 16, 22, 0, tzinfo=NEW_YORK)
    end = datetime(2026, 11, 17, 2, 0, tzinfo=NEW_YORK)
    minutes = minutes_by_local_date(start, end, NEW_YORK)
    assert minutes == {start.date(): 120, end.date(): 120}


def test_minutes_by_local_date_handles_a_spring_forward_day() -> None:
    start = datetime(2026, 3, 8, 0, 0, tzinfo=NEW_YORK)
    end = datetime(2026, 3, 9, 0, 0, tzinfo=NEW_YORK)
    minutes = minutes_by_local_date(start, end, NEW_YORK)
    assert minutes == {start.date(): 1380}  # 23 hours


def test_minutes_by_local_date_handles_a_fall_back_day() -> None:
    start = datetime(2026, 11, 1, 0, 0, tzinfo=NEW_YORK)
    end = datetime(2026, 11, 2, 0, 0, tzinfo=NEW_YORK)
    minutes = minutes_by_local_date(start, end, NEW_YORK)
    assert minutes == {start.date(): 1500}  # 25 hours


def test_measure_coverage_across_a_dst_day_uses_real_minutes() -> None:
    start = datetime(2026, 3, 8, 0, 0, tzinfo=NEW_YORK)
    end = datetime(2026, 3, 9, 0, 0, tzinfo=NEW_YORK)
    measurement = measure_coverage([(start, end, 1)], [(start, end)])
    assert measurement.required_minutes == 1380
    assert measurement.covered_minutes == 1380


def test_half_open_boundary_at_the_end_of_a_shift() -> None:
    demand = [(at(8), at(12), 1)]
    assigned = [(at(12), at(16))]
    measurement = measure_coverage(demand, assigned)
    assert measurement.covered_minutes == 0
    assert measurement.uncovered_minutes == 240
