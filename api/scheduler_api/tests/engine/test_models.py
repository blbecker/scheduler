from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
from pydantic import ValidationError

from scheduler_api.engine.models.assignment import Assignment, Individual
from scheduler_api.engine.models.population import Population
from scheduler_api.engine.models.problem import (
    JobInfo,
    SchedulingProblem,
    StaffingRequirement,
    TimeSlot,
    WorkerInfo,
)

UTC = timezone.utc


def make_slots(count: int = 4) -> tuple[TimeSlot, ...]:
    start = datetime(2026, 1, 1, 8, 0, tzinfo=UTC)
    return tuple(
        TimeSlot(
            index=index,
            start=start + timedelta(minutes=15 * index),
            end=start + timedelta(minutes=15 * (index + 1)),
        )
        for index in range(count)
    )


def make_problem() -> SchedulingProblem:
    worker_id = UUID(int=1)
    job_id = UUID(int=11)
    return SchedulingProblem(
        timezone="UTC",
        slots=make_slots(),
        staffing_requirements=tuple(
            StaffingRequirement(
                job_id=job_id,
                slot_index=index,
                required_workers=1,
            )
            for index in range(4)
        ),
        workers=(
            WorkerInfo(
                worker_id=worker_id,
                available_slot_indices=(0, 1, 2, 3),
                qualified_job_ids=(job_id,),
            ),
        ),
        jobs=(JobInfo(job_id=job_id),),
    )


def make_assignment(worker: int = 1, job: int = 11, slot: int = 0) -> Assignment:
    return Assignment(
        worker_id=UUID(int=worker),
        job_id=UUID(int=job),
        slot_index=slot,
    )


def test_time_slot_requires_timezone_aware_datetimes():
    with pytest.raises(ValidationError):
        TimeSlot(
            index=0,
            start=datetime(2026, 1, 1, 8, 0),
            end=datetime(2026, 1, 1, 8, 15),
        )


def test_time_slot_requires_positive_duration():
    with pytest.raises(ValidationError):
        TimeSlot(
            index=0,
            start=datetime(2026, 1, 1, 8, 15, tzinfo=UTC),
            end=datetime(2026, 1, 1, 8, 0, tzinfo=UTC),
        )


def test_worker_info_normalizes_collections():
    job_a = UUID(int=2)
    job_b = UUID(int=1)
    worker = WorkerInfo(
        worker_id=UUID(int=1),
        available_slot_indices=(3, 1, 3, 0),
        qualified_job_ids=(job_a, job_b, job_a),
    )

    assert worker.available_slot_indices == (0, 1, 3)
    assert tuple(job.hex for job in worker.qualified_job_ids) == tuple(
        sorted((job_a.hex, job_b.hex))
    )


def test_problem_slot_count_and_validity():
    problem = make_problem()

    assert problem.slot_count == 4


def test_problem_rejects_non_contiguous_slots():
    slots = list(make_slots())
    slots[1] = slots[1].model_copy(
        update={"start": slots[1].start + timedelta(minutes=1)}
    )

    with pytest.raises(ValidationError, match="contiguous"):
        SchedulingProblem(
            timezone="UTC",
            slots=tuple(slots),
            staffing_requirements=(),
            workers=(),
            jobs=(),
        )


def test_problem_rejects_unknown_demand_references():
    job_id = UUID(int=11)
    with pytest.raises(ValidationError, match="unknown job"):
        SchedulingProblem(
            timezone="UTC",
            slots=make_slots(),
            staffing_requirements=(
                StaffingRequirement(
                    job_id=job_id,
                    slot_index=0,
                    required_workers=1,
                ),
            ),
            workers=(),
            jobs=(),
        )


def test_problem_rejects_duplicate_demand():
    job_id = UUID(int=11)
    requirement = StaffingRequirement(
        job_id=job_id,
        slot_index=0,
        required_workers=1,
    )

    with pytest.raises(ValidationError, match="duplicate staffing"):
        SchedulingProblem(
            timezone="UTC",
            slots=make_slots(),
            staffing_requirements=(requirement, requirement),
            workers=(),
            jobs=(JobInfo(job_id=job_id),),
        )


def test_problem_rejects_worker_availability_out_of_range():
    job_id = UUID(int=11)
    with pytest.raises(ValidationError, match="unknown slot"):
        SchedulingProblem(
            timezone="UTC",
            slots=make_slots(),
            staffing_requirements=(),
            workers=(
                WorkerInfo(
                    worker_id=UUID(int=1),
                    available_slot_indices=(4,),
                    qualified_job_ids=(job_id,),
                ),
            ),
            jobs=(JobInfo(job_id=job_id),),
        )


def test_individual_canonicalizes_assignments():
    individual = Individual(
        id=UUID(int=100),
        assignments=(
            make_assignment(slot=2),
            make_assignment(slot=0),
            make_assignment(slot=1),
        ),
    )

    assert [item.slot_index for item in individual.assignments] == [0, 1, 2]
    assert individual.feasible


def test_individual_rejects_duplicate_assignments():
    assignment = make_assignment()

    with pytest.raises(ValidationError, match="duplicate assignments"):
        Individual(id=UUID(int=100), assignments=(assignment, assignment))


def test_individual_scores_must_be_finite():
    with pytest.raises(ValidationError):
        Individual(
            id=UUID(int=100),
            assignments=(),
            scores={"coverage": float("nan")},
        )


def test_population_rejects_duplicate_individual_ids():
    individual = Individual(id=UUID(int=100), assignments=())

    with pytest.raises(ValidationError, match="duplicate individual IDs"):
        Population(individuals=(individual, individual))


def test_frozen_models_reject_mutation():
    individual = Individual(id=UUID(int=100), assignments=())

    with pytest.raises(ValidationError):
        individual.id = UUID(int=101)
