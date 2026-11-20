from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import Field, model_validator

from .assignment import Individual
from .base import EngineModel
from .phase import PhaseType
from .population import Population
from .problem import SchedulingProblem


class ExecutionStatus(StrEnum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScoreTarget(StrEnum):
    POPULATION = "population"
    OFFSPRING = "offspring"


class FailureInfo(EngineModel):
    error_type: str
    message: str
    phase: PhaseType | None = None
    component_id: str | None = None
    invocation_id: UUID | None = None


class ExecutionState(EngineModel):
    execution_id: UUID
    problem: SchedulingProblem
    status: ExecutionStatus = ExecutionStatus.RUNNING
    generation: int = Field(default=0, ge=0)

    population: Population
    selected_parents: Population | None = None
    offspring: Population | None = None
    score_target: ScoreTarget | None = None

    best_individual: Individual | None = None
    best_total_score: float | None = None
    elite_individuals: tuple[Individual, ...] = ()

    termination_reason: str | None = None
    failure: FailureInfo | None = None

    @model_validator(mode="after")
    def _validate_status(self) -> ExecutionState:
        if self.status is ExecutionStatus.COMPLETED:
            if self.failure is not None:
                raise ValueError("completed execution cannot have a failure")
            if self.termination_reason is None:
                raise ValueError("completed execution requires a termination reason")
        elif self.status is ExecutionStatus.FAILED:
            if self.failure is None:
                raise ValueError("failed execution requires failure info")
        elif self.failure is not None:
            raise ValueError("running execution cannot have a failure")
        return self
