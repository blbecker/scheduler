from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from scheduler_api.engine.models.problem import TimeSlot
from scheduler_api.mappers.assignment_shift_mapper import coalesce_assignments
from scheduler_api.tests.engine.factories import (
    UTC,
    make_assignment,
    make_individual,
    make_job,
    make_problem,
    make_slots,
    make_worker,
)


def make_mapper_problem(slots: tuple[TimeSlot, ...]):
    return make_problem(
        slots=slots,
        workers=(
            make_worker(
                worker_id=1,
                job_ids=(11, 12),
                slot_indices=tuple(range(len(slots))),
            ),
            make_worker(
                worker_id=2,
                job_ids=(11, 12),
                slot_indices=tuple(range(len(slots))),
            ),
        ),
        jobs=(make_job(11), make_job(12)),
        staffing_requirements=(),
    )


def test_contiguous_assignments_coalesce_to_one_shift():
    problem = make_mapper_problem(make_slots(4))
    individual = make_individual(
        assignments=tuple(make_assignment(slot_index=index) for index in range(4))
    )

    shifts = coalesce_assignments(problem, individual)

    assert len(shifts) == 1
    shift = shifts[0]
    assert shift.start == datetime(2026, 1, 1, 8, 0, tzinfo=UTC)
    assert shift.end == datetime(2026, 1, 1, 9, 0, tzinfo=UTC)
    assert shift.slot_indices == (0, 1, 2, 3)


def test_gap_splits_into_two_shifts():
    problem = make_mapper_problem(make_slots(5))
    individual = make_individual(
        assignments=tuple(make_assignment(slot_index=index) for index in (0, 1, 3, 4))
    )

    shifts = coalesce_assignments(problem, individual)

    assert [shift.slot_indices for shift in shifts] == [(0, 1), (3, 4)]
    assert shifts[0].start == datetime(2026, 1, 1, 8, 0, tzinfo=UTC)
    assert shifts[0].end == datetime(2026, 1, 1, 8, 30, tzinfo=UTC)
    assert shifts[1].start == datetime(2026, 1, 1, 8, 45, tzinfo=UTC)


def test_job_change_splits_into_two_shifts():
    problem = make_mapper_problem(make_slots(4))
    individual = make_individual(
        assignments=(
            make_assignment(job_id=11, slot_index=0),
            make_assignment(job_id=11, slot_index=1),
            make_assignment(job_id=12, slot_index=2),
            make_assignment(job_id=12, slot_index=3),
        )
    )

    shifts = coalesce_assignments(problem, individual)

    assert len(shifts) == 2
    assert {shift.job_id for shift in shifts} == {
        make_job(11).job_id,
        make_job(12).job_id,
    }


def test_worker_change_splits_into_separate_shifts():
    problem = make_mapper_problem(make_slots(4))
    individual = make_individual(
        assignments=(
            make_assignment(worker_id=1, slot_index=0),
            make_assignment(worker_id=1, slot_index=1),
            make_assignment(worker_id=2, slot_index=2),
            make_assignment(worker_id=2, slot_index=3),
        )
    )

    shifts = coalesce_assignments(problem, individual)

    assert len(shifts) == 2
    assert {shift.worker_id for shift in shifts} == {
        make_worker(worker_id=1).worker_id,
        make_worker(worker_id=2).worker_id,
    }


def test_actual_slot_timestamps_are_used():
    start = datetime(2026, 6, 1, 8, 0, tzinfo=UTC)
    slots = (
        TimeSlot(
            index=0,
            start=start,
            end=start + timedelta(minutes=7),
        ),
        TimeSlot(
            index=1,
            start=start + timedelta(minutes=7),
            end=start + timedelta(minutes=30),
        ),
        TimeSlot(
            index=2,
            start=start + timedelta(minutes=30),
            end=start + timedelta(minutes=77),
        ),
    )
    problem = make_mapper_problem(slots)
    individual = make_individual(
        assignments=tuple(make_assignment(slot_index=index) for index in range(3))
    )

    shifts = coalesce_assignments(problem, individual)

    assert len(shifts) == 1
    assert shifts[0].start == slots[0].start
    assert shifts[0].end == slots[-1].end
    assert shifts[0].slot_indices == (0, 1, 2)


def test_duplicate_assignments_are_deduplicated_defensively():
    problem = make_mapper_problem(make_slots(2))
    assignment = make_assignment(slot_index=0)
    individual = make_individual().model_copy(
        update={"assignments": (assignment, assignment)}
    )

    shifts = coalesce_assignments(problem, individual)

    assert len(shifts) == 1
    assert shifts[0].slot_indices == (0,)


def test_out_of_range_slot_raises_value_error():
    problem = make_mapper_problem(make_slots(2))
    individual = make_individual(assignments=(make_assignment(slot_index=2),))

    with pytest.raises(ValueError):
        coalesce_assignments(problem, individual)


def test_empty_individual_produces_no_shifts():
    problem = make_mapper_problem(make_slots(2))

    assert coalesce_assignments(problem, make_individual()) == ()


def test_output_is_sorted_by_start_then_worker_and_job():
    problem = make_mapper_problem(make_slots(2))
    individual = make_individual(
        assignments=(
            make_assignment(worker_id=2, job_id=12, slot_index=0),
            make_assignment(worker_id=1, job_id=12, slot_index=0),
            make_assignment(worker_id=2, job_id=11, slot_index=0),
            make_assignment(worker_id=1, job_id=11, slot_index=0),
        )
    )

    shifts = coalesce_assignments(problem, individual)

    assert [(shift.worker_id.int, shift.job_id.int) for shift in shifts] == [
        (1, 11),
        (1, 12),
        (2, 11),
        (2, 12),
    ]


def test_coalesced_shift_is_frozen():
    problem = make_mapper_problem(make_slots(1))
    individual = make_individual(assignments=(make_assignment(slot_index=0),))
    shift = coalesce_assignments(problem, individual)[0]

    with pytest.raises(ValidationError):
        shift.worker_id = make_worker(2).worker_id
