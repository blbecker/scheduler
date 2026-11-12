"""Problem context: the immutable input to one execution."""

from __future__ import annotations

from datetime import datetime, timedelta, tzinfo
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, model_validator

from scheduler_api.engine.errors import ProblemValidationError
from scheduler_api.engine.models.time import (
    TimeWindow,
    ensure_aware,
    ensure_minute_aligned,
    to_utc,
)


class ShiftLengthPolicy(BaseModel):
    """Organization-level hard shift-length limits, in minutes."""

    model_config = ConfigDict(frozen=True)

    minimum_minutes: int = Field(default=120, ge=1)
    maximum_minutes: int = Field(default=720, ge=1)

    @model_validator(mode="after")
    def _validate(self) -> "ShiftLengthPolicy":
        if self.maximum_minutes < self.minimum_minutes:
            raise ValueError("maximum_minutes must be >= minimum_minutes")
        return self


class ScheduleLimits(BaseModel):
    """Organization-level hard caps. ``None`` means no limit is configured."""

    model_config = ConfigDict(frozen=True)

    maximum_hours_per_week: int | None = Field(default=None, ge=1)
    maximum_shifts_per_day: int | None = Field(default=None, ge=1)


class CoverageRequirement(BaseModel):
    """Required headcount for one job during one window.

    Deliberately has no identity field: coverage is measured per (job, instant)
    as a sum over active windows, and nothing in the engine records which
    requirement a shift serves.
    """

    model_config = ConfigDict(frozen=True)

    job_id: UUID
    start: datetime
    end: datetime
    required_workers: int = Field(ge=1)

    @model_validator(mode="after")
    def _validate(self) -> "CoverageRequirement":
        ensure_aware(self.start, "start")
        ensure_aware(self.end, "end")
        ensure_minute_aligned(self.start, "start")
        ensure_minute_aligned(self.end, "end")
        if self.end <= self.start:
            raise ValueError("requirement end must be strictly after start")
        return self

    @property
    def minutes(self) -> int:
        return int((to_utc(self.end) - to_utc(self.start)).total_seconds() // 60)


class WorkerInfo(BaseModel):
    """Everything the engine knows about one worker."""

    model_config = ConfigDict(frozen=True)

    worker_id: UUID
    qualified_job_ids: frozenset[UUID]
    available_windows: tuple[TimeWindow, ...]

    #: Hard overrides of :class:`ShiftLengthPolicy`. ``None`` means "use policy".
    minimum_shift_minutes: int | None = Field(default=None, ge=1)
    maximum_shift_minutes: int | None = Field(default=None, ge=1)

    #: Soft preferences. Scored, never enforced.
    preferred_minimum_shift_minutes: int | None = Field(default=None, ge=1)
    preferred_maximum_shift_minutes: int | None = Field(default=None, ge=1)


class JobInfo(BaseModel):
    """A job (role). Owns exactly one skill set, expressed as qualifications."""

    model_config = ConfigDict(frozen=True)

    job_id: UUID
    name: str


class SchedulingProblem(BaseModel):
    """The immutable input to one execution."""

    model_config = ConfigDict(frozen=True)

    timezone: str
    horizon_start: datetime
    horizon_end: datetime
    boundary_granularity_minutes: int = Field(default=15, ge=1)
    shifts: ShiftLengthPolicy = Field(default_factory=ShiftLengthPolicy)
    limits: ScheduleLimits = Field(default_factory=ScheduleLimits)
    requirements: tuple[CoverageRequirement, ...]
    workers: tuple[WorkerInfo, ...]
    jobs: tuple[JobInfo, ...]

    @model_validator(mode="after")
    def _validate(self) -> "SchedulingProblem":
        ensure_aware(self.horizon_start, "horizon_start")
        ensure_aware(self.horizon_end, "horizon_end")
        ensure_minute_aligned(self.horizon_start, "horizon_start")
        ensure_minute_aligned(self.horizon_end, "horizon_end")
        if self.horizon_end <= self.horizon_start:
            raise ValueError("horizon_end must be strictly after horizon_start")
        ZoneInfo(self.timezone)  # raises if the tz is unknown
        return self

    @property
    def tz(self) -> tzinfo:
        return ZoneInfo(self.timezone)

    @property
    def horizon_minutes(self) -> int:
        return int(
            (to_utc(self.horizon_end) - to_utc(self.horizon_start)).total_seconds()
            // 60
        )

    def worker(self, worker_id: UUID) -> WorkerInfo | None:
        for worker in self.workers:
            if worker.worker_id == worker_id:
                return worker
        return None

    def job(self, job_id: UUID) -> JobInfo | None:
        for job in self.jobs:
            if job.job_id == job_id:
                return job
        return None

    def requirements_for_job(self, job_id: UUID) -> tuple[CoverageRequirement, ...]:
        return tuple(req for req in self.requirements if req.job_id == job_id)

    def requirements_covering(
        self, moment: datetime
    ) -> tuple[CoverageRequirement, ...]:
        return tuple(req for req in self.requirements if req.start <= moment < req.end)


def validate_problem_context(problem: SchedulingProblem) -> None:
    """Cross-entity validation. Called at the execution boundary.

    Raises :class:`ProblemValidationError` with a human-readable reason.
    """

    if not problem.requirements:
        raise ProblemValidationError("the problem declares no coverage requirements")
    if not problem.workers:
        raise ProblemValidationError("the problem declares no workers")

    job_ids = [job.job_id for job in problem.jobs]
    if len(set(job_ids)) != len(job_ids):
        raise ProblemValidationError("job ids must be unique")
    worker_ids = [worker.worker_id for worker in problem.workers]
    if len(set(worker_ids)) != len(worker_ids):
        raise ProblemValidationError("worker ids must be unique")

    known_jobs = set(job_ids)
    for requirement in problem.requirements:
        if requirement.job_id not in known_jobs:
            raise ProblemValidationError(
                f"coverage requirement references unknown job {requirement.job_id}"
            )
        if (
            requirement.start < problem.horizon_start
            or requirement.end > problem.horizon_end
        ):
            raise ProblemValidationError(
                f"coverage requirement for job {requirement.job_id} falls outside the horizon"
            )

    for worker in problem.workers:
        unknown = worker.qualified_job_ids - known_jobs
        if unknown:
            raise ProblemValidationError(
                f"worker {worker.worker_id} is qualified for unknown jobs {sorted(map(str, unknown))}"
            )
        if (
            worker.minimum_shift_minutes is not None
            and worker.maximum_shift_minutes is not None
            and worker.maximum_shift_minutes < worker.minimum_shift_minutes
        ):
            raise ProblemValidationError(
                f"worker {worker.worker_id} has maximum_shift_minutes below minimum_shift_minutes"
            )
        for window in worker.available_windows:
            if window.end < problem.horizon_start - timedelta(
                days=1
            ) or window.start > problem.horizon_end + timedelta(days=1):
                raise ProblemValidationError(
                    f"worker {worker.worker_id} has availability windows unrelated to the horizon"
                )
