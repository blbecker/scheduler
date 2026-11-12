"""The genome: planned shifts, individuals, and populations."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from scheduler_api.engine.models.scores import SCORE_MAX, SCORE_MIN, Violation
from scheduler_api.engine.models.time import ensure_aware, ensure_minute_aligned, to_utc


def _shift_sort_key(shift: "PlannedShift") -> tuple[str, datetime, str, str]:
    return (
        str(shift.worker_id),
        to_utc(shift.start),
        str(shift.job_id),
        str(shift.shift_id),
    )


class PlannedShift(BaseModel):
    """One contiguous interval of work for one worker on one job.

    Named ``PlannedShift`` rather than ``Shift`` so it never shadows the ORM
    entity of that name.
    """

    model_config = ConfigDict(frozen=True)

    shift_id: UUID
    worker_id: UUID
    job_id: UUID
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def _validate(self) -> "PlannedShift":
        ensure_aware(self.start, "start")
        ensure_aware(self.end, "end")
        ensure_minute_aligned(self.start, "start")
        ensure_minute_aligned(self.end, "end")
        if to_utc(self.end) <= to_utc(self.start):
            raise ValueError("shift end must be strictly after start")
        return self

    @property
    def minutes(self) -> int:
        return int((to_utc(self.end) - to_utc(self.start)).total_seconds() // 60)


class Individual(BaseModel):
    """One candidate schedule.

    Shifts are canonicalized on construction so two structurally identical
    individuals compare and serialize identically.
    """

    model_config = ConfigDict(frozen=True)

    id: UUID
    shifts: tuple[PlannedShift, ...] = ()
    scores: dict[str, float] = Field(default_factory=dict)
    violations: tuple[Violation, ...] = ()
    fitness: float | None = None

    @model_validator(mode="after")
    def _normalize(self) -> "Individual":
        object.__setattr__(
            self, "shifts", tuple(sorted(self.shifts, key=_shift_sort_key))
        )
        for component_id, value in self.scores.items():
            if not SCORE_MIN <= value <= SCORE_MAX:
                raise ValueError(
                    f"score for component {component_id!r} is outside [0, 100]: {value}"
                )
        if self.fitness is not None and not SCORE_MIN <= self.fitness <= SCORE_MAX:
            raise ValueError(f"fitness is outside [0, 100]: {self.fitness}")
        return self

    @property
    def feasible(self) -> bool:
        """A candidate is feasible if and only if it carries no violations."""
        return not self.violations

    @property
    def structural_key(self) -> tuple[tuple[str, datetime, datetime, str], ...]:
        """Identity of the schedule itself, ignoring ids, scores, and violations."""
        return tuple(
            (
                str(shift.worker_id),
                to_utc(shift.start),
                to_utc(shift.end),
                str(shift.job_id),
            )
            for shift in self.shifts
        )

    def with_evaluation(
        self,
        *,
        scores: dict[str, float],
        violations: tuple[Violation, ...],
        fitness: float | None,
    ) -> "Individual":
        """Return a copy carrying evaluation results."""
        return self.model_copy(
            update={"scores": scores, "violations": violations, "fitness": fitness}
        )


class Population(BaseModel):
    """An immutable collection of candidates."""

    model_config = ConfigDict(frozen=True)

    individuals: tuple[Individual, ...] = ()

    @model_validator(mode="after")
    def _validate(self) -> "Population":
        ids = [individual.id for individual in self.individuals]
        if len(set(ids)) != len(ids):
            raise ValueError("individual ids must be unique within a population")
        return self

    def __len__(self) -> int:
        return len(self.individuals)
