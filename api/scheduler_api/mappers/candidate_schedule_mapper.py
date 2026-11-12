"""Map engine candidates onto persistence-ready drafts.

The engine returns engine DTOs and knows nothing about the database. This module is
the seam between the two. It deliberately does **not** construct SQLModel objects:
the persistence model still has no ``Schedule``/``Job`` entities or demand tables
(see ``DESIGN.md``, section 21), so the mapper produces validated, plain drafts that
a service can persist once that schema lands.

Nothing here belongs inside ``engine/``.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from scheduler_api.engine.models.problem import SchedulingProblem
from scheduler_api.engine.models.results import CandidateSchedule, ExecutionResult
from scheduler_api.engine.models.scores import Violation, ViolationCode

#: How many human-readable examples of each violation code to keep.
DEFAULT_EXAMPLE_LIMIT = 3

#: Short human explanations, so a reviewer does not need the code catalogue.
CODE_TITLES: dict[ViolationCode, str] = {
    ViolationCode.WORKER_UNAVAILABLE: "worker unavailable",
    ViolationCode.WORKER_UNQUALIFIED: "worker not qualified",
    ViolationCode.WORKER_DOUBLE_BOOKED: "worker double-booked",
    ViolationCode.SHIFT_TOO_SHORT: "shift too short",
    ViolationCode.SHIFT_TOO_LONG: "shift too long",
    ViolationCode.SHIFT_OUTSIDE_DEMAND: "shift serves no demand",
    ViolationCode.WEEKLY_HOURS_EXCEEDED: "weekly hours exceeded",
    ViolationCode.SHIFTS_PER_DAY_EXCEEDED: "too many shifts in a day",
    ViolationCode.UNKNOWN_REFERENCE: "unknown worker or job",
}


class ShiftDraft(BaseModel):
    """One shift, ready to become a persisted ``Shift`` row."""

    model_config = ConfigDict(frozen=True)

    shift_id: UUID
    worker_id: UUID
    job_id: UUID
    start: datetime
    end: datetime
    duration_minutes: int = Field(ge=1)


class ViolationSummary(BaseModel):
    """A violation code collapsed into counts plus a few examples."""

    model_config = ConfigDict(frozen=True)

    code: ViolationCode
    title: str
    count: int = Field(ge=1)
    worker_ids: tuple[UUID, ...] = ()
    job_ids: tuple[UUID, ...] = ()
    examples: tuple[str, ...] = ()


class ScheduleDraft(BaseModel):
    """A candidate schedule with its review basis, ready to be persisted."""

    model_config = ConfigDict(frozen=True)

    execution_id: UUID
    candidate_id: UUID
    rank: int = Field(ge=1)
    timezone: str
    horizon_start: datetime
    horizon_end: datetime
    fitness: float = Field(ge=0.0, le=100.0)
    feasible: bool
    scores: dict[str, float] = Field(default_factory=dict)
    shifts: tuple[ShiftDraft, ...] = ()
    violations: tuple[ViolationSummary, ...] = ()
    violation_count: int = Field(default=0, ge=0)
    termination_reason: str
    random_seed: int


def _describe(violation: Violation) -> str:
    parts: list[str] = [CODE_TITLES.get(violation.code, violation.code.value)]
    if violation.worker_id is not None:
        parts.append(f"worker={violation.worker_id}")
    if violation.job_id is not None:
        parts.append(f"job={violation.job_id}")
    if violation.start is not None and violation.end is not None:
        parts.append(f"{violation.start.isoformat()}..{violation.end.isoformat()}")
    elif violation.start is not None:
        parts.append(violation.start.isoformat())
    if violation.detail:
        parts.append(violation.detail)
    return " | ".join(parts)


def summarise_violations(
    violations: tuple[Violation, ...], *, example_limit: int = DEFAULT_EXAMPLE_LIMIT
) -> tuple[ViolationSummary, ...]:
    """Group raw violations by code, keeping counts, entities, and a few examples.

    A single infeasible schedule can carry thousands of raw violations; a reviewer
    needs counts and representative cases, not the dump.
    """
    grouped: dict[ViolationCode, list[Violation]] = {}
    for violation in violations:
        grouped.setdefault(violation.code, []).append(violation)
    summaries = [
        ViolationSummary(
            code=code,
            title=CODE_TITLES.get(code, code.value),
            count=len(found),
            worker_ids=tuple(
                sorted(
                    {violation.worker_id for violation in found if violation.worker_id}
                )
            ),
            job_ids=tuple(
                sorted({violation.job_id for violation in found if violation.job_id})
            ),
            examples=tuple(_describe(violation) for violation in found[:example_limit]),
        )
        for code, found in grouped.items()
    ]
    return tuple(
        sorted(summaries, key=lambda summary: (-summary.count, summary.code.value))
    )


def to_schedule_draft(
    candidate: CandidateSchedule,
    result: ExecutionResult,
    problem: SchedulingProblem,
    *,
    example_limit: int = DEFAULT_EXAMPLE_LIMIT,
) -> ScheduleDraft:
    """Convert one engine candidate into a persistence-ready draft."""
    shifts = tuple(
        ShiftDraft(
            shift_id=shift.shift_id,
            worker_id=shift.worker_id,
            job_id=shift.job_id,
            start=shift.start,
            end=shift.end,
            duration_minutes=shift.minutes,
        )
        for shift in candidate.shifts
    )
    return ScheduleDraft(
        execution_id=result.execution_id,
        candidate_id=candidate.candidate_id,
        rank=candidate.rank,
        timezone=problem.timezone,
        horizon_start=problem.horizon_start,
        horizon_end=problem.horizon_end,
        fitness=candidate.fitness,
        feasible=candidate.feasible,
        scores=dict(candidate.scores),
        shifts=shifts,
        violations=summarise_violations(
            candidate.violations, example_limit=example_limit
        ),
        violation_count=len(candidate.violations),
        termination_reason=result.termination_reason,
        random_seed=result.random_seed,
    )
