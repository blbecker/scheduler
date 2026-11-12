"""Small deterministic fixtures for engine tests."""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from scheduler_api.engine.models.genome import Individual, PlannedShift
from scheduler_api.engine.models.problem import (
    CoverageRequirement,
    JobInfo,
    ScheduleLimits,
    SchedulingProblem,
    ShiftLengthPolicy,
    TimeWindow,
    WorkerInfo,
)
from scheduler_api.engine.models.scores import Violation

TZ = ZoneInfo("America/Puerto_Rico")
#: Local midnight, 2026-11-16 (a Monday).
BASE = datetime(2026, 11, 16, 0, 0, tzinfo=TZ)

JOB_COOK = UUID(int=101)
JOB_HOST = UUID(int=102)

WORKER_1 = UUID(int=1)
WORKER_2 = UUID(int=2)
WORKER_3 = UUID(int=3)
WORKER_4 = UUID(int=4)


def at(hours: float, *, day: int = 0) -> datetime:
    """A horizon-relative instant, in hours."""
    return BASE + timedelta(days=day, hours=hours)


def make_window(start_hours: float, end_hours: float, *, day: int = 0) -> TimeWindow:
    return TimeWindow(start=at(start_hours, day=day), end=at(end_hours, day=day))


def make_shift(
    worker_id: UUID,
    job_id: UUID,
    start_hours: float,
    end_hours: float,
    *,
    day: int = 0,
    shift_id: UUID | None = None,
) -> PlannedShift:
    return PlannedShift(
        shift_id=shift_id or UUID(int=9000 + int(start_hours) * 60 + int(end_hours)),
        worker_id=worker_id,
        job_id=job_id,
        start=at(start_hours, day=day),
        end=at(end_hours, day=day),
    )


def make_individual(
    shifts: tuple[PlannedShift, ...] = (),
    *,
    individual_id: UUID | None = None,
    scores: dict[str, float] | None = None,
    violations: tuple[Violation, ...] = (),
    fitness: float | None = None,
) -> Individual:
    return Individual(
        id=individual_id or UUID(int=500 + len(shifts)),
        shifts=shifts,
        scores=scores or {},
        violations=violations,
        fitness=fitness,
    )


def make_worker(
    worker_id: UUID,
    *,
    jobs: frozenset[UUID] | None = None,
    availability: tuple[TimeWindow, ...] | None = None,
    minimum_shift_minutes: int | None = None,
    maximum_shift_minutes: int | None = None,
    preferred_minimum_shift_minutes: int | None = None,
    preferred_maximum_shift_minutes: int | None = None,
) -> WorkerInfo:
    return WorkerInfo(
        worker_id=worker_id,
        qualified_job_ids=jobs if jobs is not None else frozenset({JOB_COOK, JOB_HOST}),
        available_windows=(
            availability
            if availability is not None
            else (make_window(0, 24), make_window(0, 24, day=1))
        ),
        minimum_shift_minutes=minimum_shift_minutes,
        maximum_shift_minutes=maximum_shift_minutes,
        preferred_minimum_shift_minutes=preferred_minimum_shift_minutes,
        preferred_maximum_shift_minutes=preferred_maximum_shift_minutes,
    )


def make_problem(
    *,
    requirements: tuple[CoverageRequirement, ...] | None = None,
    workers: tuple[WorkerInfo, ...] | None = None,
    jobs: tuple[JobInfo, ...] | None = None,
    policy: ShiftLengthPolicy | None = None,
    limits: ScheduleLimits | None = None,
    granularity: int = 15,
    horizon_days: int = 2,
) -> SchedulingProblem:
    return SchedulingProblem(
        timezone="America/Puerto_Rico",
        horizon_start=BASE,
        horizon_end=BASE + timedelta(days=horizon_days),
        boundary_granularity_minutes=granularity,
        shifts=policy or ShiftLengthPolicy(),
        limits=limits or ScheduleLimits(),
        requirements=(
            requirements
            if requirements is not None
            else (
                CoverageRequirement(
                    job_id=JOB_COOK, start=at(8), end=at(16), required_workers=2
                ),
            )
        ),
        workers=(
            workers
            if workers is not None
            else (
                make_worker(WORKER_1),
                make_worker(WORKER_2),
                make_worker(WORKER_3),
                make_worker(WORKER_4),
            )
        ),
        jobs=(
            jobs
            if jobs is not None
            else (
                JobInfo(job_id=JOB_COOK, name="Cook"),
                JobInfo(job_id=JOB_HOST, name="Host"),
            )
        ),
    )


def rule(code: str, *, worker_id: UUID | None = None) -> Violation:
    """A violation with a given code, for feasibility tests."""
    from scheduler_api.engine.models.scores import ViolationCode

    return Violation(code=ViolationCode(code), worker_id=worker_id, detail="test")
