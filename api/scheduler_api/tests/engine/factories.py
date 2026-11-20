from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from scheduler_api.engine.models.assignment import Assignment, Individual
from scheduler_api.engine.models.problem import (
    JobInfo,
    SchedulingProblem,
    StaffingRequirement,
    TimeSlot,
    WorkerInfo,
)
from scheduler_api.engine.models.scores import ScorerWeight, ScoringPolicy

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


def make_worker(
    worker_id: int = 1,
    job_ids: tuple[int, ...] = (11,),
    slot_indices: tuple[int, ...] = (0, 1, 2, 3),
    minimum: int | None = None,
    maximum: int | None = None,
) -> WorkerInfo:
    return WorkerInfo(
        worker_id=UUID(int=worker_id),
        available_slot_indices=slot_indices,
        qualified_job_ids=tuple(UUID(int=job_id) for job_id in job_ids),
        minimum_shift_slots=minimum,
        maximum_shift_slots=maximum,
    )


def make_job(job_id: int = 11) -> JobInfo:
    return JobInfo(job_id=UUID(int=job_id))


def make_demand(
    job_id: int = 11, slot_index: int = 0, required_workers: int = 1
) -> StaffingRequirement:
    return StaffingRequirement(
        job_id=UUID(int=job_id),
        slot_index=slot_index,
        required_workers=required_workers,
    )


def make_problem(
    *,
    slots: tuple[TimeSlot, ...] | None = None,
    workers: tuple[WorkerInfo, ...] | None = None,
    jobs: tuple[JobInfo, ...] | None = None,
    staffing_requirements: tuple[StaffingRequirement, ...] | None = None,
    timezone_name: str = "UTC",
) -> SchedulingProblem:
    slot_rows = slots if slots is not None else make_slots()
    job_rows = jobs if jobs is not None else (make_job(),)
    worker_rows = workers if workers is not None else (make_worker(),)
    demand_rows = (
        staffing_requirements
        if staffing_requirements is not None
        else tuple(make_demand(slot_index=index) for index in range(len(slot_rows)))
    )
    return SchedulingProblem(
        timezone=timezone_name,
        slots=slot_rows,
        staffing_requirements=demand_rows,
        workers=worker_rows,
        jobs=job_rows,
    )


def make_assignment(
    worker_id: int = 1, job_id: int = 11, slot_index: int = 0
) -> Assignment:
    return Assignment(
        worker_id=UUID(int=worker_id),
        job_id=UUID(int=job_id),
        slot_index=slot_index,
    )


def make_individual(
    individual_id: int = 100,
    assignments: tuple[Assignment, ...] = (),
    scores: dict[str, float] | None = None,
) -> Individual:
    return Individual(
        id=UUID(int=individual_id),
        assignments=assignments,
        scores=scores or {},
    )


def make_policy(
    *weights: tuple[str, float],
) -> ScoringPolicy:
    rows = weights or (("coverage", 1.0),)
    return ScoringPolicy(
        weights=tuple(
            ScorerWeight(component_id=component_id, weight=weight)
            for component_id, weight in rows
        )
    )
