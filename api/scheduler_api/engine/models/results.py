"""Execution results: ranked candidate schedules."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from scheduler_api.engine.models.genome import PlannedShift
from scheduler_api.engine.models.scores import Violation


class CandidateSchedule(BaseModel):
    """One schedule the engine offers for review."""

    model_config = ConfigDict(frozen=True)

    candidate_id: UUID
    rank: int = Field(ge=1)
    shifts: tuple[PlannedShift, ...] = ()
    fitness: float = Field(ge=0.0, le=100.0)
    scores: dict[str, float] = Field(default_factory=dict)
    violations: tuple[Violation, ...] = ()
    feasible: bool


class ExecutionResult(BaseModel):
    """The outcome of one execution."""

    model_config = ConfigDict(frozen=True)

    execution_id: UUID
    candidates: tuple[CandidateSchedule, ...] = ()
    generation: int = Field(ge=0)
    termination_reason: str
    random_seed: int
