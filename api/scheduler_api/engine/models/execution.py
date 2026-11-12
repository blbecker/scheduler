"""Execution request, state, and status."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from scheduler_api.engine.models.config import (
    CullerConfig,
    MutatorConfig,
    ScorerConfig,
    SeederConfig,
    SelectorConfig,
    StopperConfig,
)
from scheduler_api.engine.models.fitness import FitnessConfig
from scheduler_api.engine.models.genome import Individual, Population
from scheduler_api.engine.models.phase import PhasePlan
from scheduler_api.engine.models.problem import SchedulingProblem


class ExecutionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScoringTarget(StrEnum):
    """Which candidate set a SCORE phase is evaluating."""

    POPULATION = "population"
    OFFSPRING = "offspring"


class SolverSettings(BaseModel):
    """The GA configuration a solver hands to an execution."""

    model_config = ConfigDict(frozen=True)

    population_size: int = Field(ge=1)
    parent_count: int = Field(ge=1)
    offspring_count: int = Field(ge=1)
    max_candidates: int = Field(default=1, ge=1)
    preserve_best: int = Field(default=1, ge=0)
    fitness: FitnessConfig = Field(default_factory=FitnessConfig)
    seeders: tuple[SeederConfig, ...]
    scorers: tuple[ScorerConfig, ...]
    selector: SelectorConfig
    mutators: tuple[MutatorConfig, ...]
    culler: CullerConfig
    stoppers: tuple[StopperConfig, ...]

    @model_validator(mode="after")
    def _validate(self) -> "SolverSettings":
        if not self.seeders:
            raise ValueError("at least one seeder is required")
        if not self.scorers:
            raise ValueError("at least one scorer is required")
        if not self.mutators:
            raise ValueError("at least one mutator is required")
        if not self.stoppers:
            raise ValueError("at least one stopper is required")
        seeded = sum(seeder.contribution for seeder in self.seeders)
        if seeded != self.population_size:
            raise ValueError(
                f"seeder contributions sum to {seeded}, expected population_size {self.population_size}"
            )
        shared = sum(mutator.share for mutator in self.mutators)
        if shared != self.offspring_count:
            raise ValueError(
                f"mutator shares sum to {shared}, expected offspring_count {self.offspring_count}"
            )
        if self.parent_count > self.population_size:
            raise ValueError("parent_count must not exceed population_size")
        if self.preserve_best > self.population_size:
            raise ValueError("preserve_best must not exceed population_size")
        return self

    def weight_for(self, component_id: str) -> float:
        return self.fitness.weight_for(component_id)


class ExecutionRequest(BaseModel):
    """Everything needed to run one execution."""

    model_config = ConfigDict(frozen=True)

    execution_id: UUID
    problem: SchedulingProblem
    random_seed: int
    settings: SolverSettings


class ExecutionState(BaseModel):
    """Explicit, serializable algorithm state.

    The controller holds no per-execution attributes; everything needed to resume
    or replay an execution lives here.
    """

    model_config = ConfigDict(frozen=True)

    execution_id: UUID
    status: ExecutionStatus = ExecutionStatus.PENDING
    generation: int = 0
    population: Population = Field(default_factory=Population)
    best_so_far: Individual | None = None
    selected: tuple[Individual, ...] = ()
    offspring: tuple[Individual, ...] = ()
    termination_reason: str | None = None
    failure_reason: str | None = None
    completed_phase_ids: tuple[UUID, ...] = ()
    next_plan: PhasePlan | None = None
    scoring_target: ScoringTarget | None = None

    def completed(self, phase_execution_id: UUID) -> bool:
        return phase_execution_id in self.completed_phase_ids

    def with_phase_completed(self, phase_execution_id: UUID) -> "ExecutionState":
        return self.model_copy(
            update={
                "completed_phase_ids": (*self.completed_phase_ids, phase_execution_id)
            }
        )
