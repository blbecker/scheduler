from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field

from .assignment import Individual
from .base import EngineModel
from .population import Population
from .problem import SchedulingProblem
from .scores import ScoringPolicy, Violation


class SeedInput(EngineModel):
    category: Literal["seeder"]
    problem: SchedulingProblem
    population_size: int = Field(ge=1)
    rng_seed: int = Field(ge=0)


class SeedResult(EngineModel):
    category: Literal["seeder"]
    population: Population


class ScoreInput(EngineModel):
    category: Literal["scorer"]
    problem: SchedulingProblem
    population: Population


class ScoreUpdate(EngineModel):
    individual_id: UUID
    score: float
    violations: tuple[Violation, ...] = ()


class ScoreResult(EngineModel):
    category: Literal["scorer"]
    updates: tuple[ScoreUpdate, ...]


class SelectInput(EngineModel):
    category: Literal["selector"]
    population: Population
    count: int = Field(ge=0)
    scoring_policy: ScoringPolicy


class SelectResult(EngineModel):
    category: Literal["selector"]
    selected: Population


class MutateInput(EngineModel):
    category: Literal["mutator"]
    problem: SchedulingProblem
    parents: Population
    offspring_count: int = Field(ge=0)
    rng_seed: int = Field(ge=0)


class MutateResult(EngineModel):
    category: Literal["mutator"]
    offspring: Population


class CullInput(EngineModel):
    category: Literal["culler"]
    population: Population
    target_size: int = Field(ge=1)
    scoring_policy: ScoringPolicy
    elite_individuals: tuple[Individual, ...] = ()


class CullResult(EngineModel):
    category: Literal["culler"]
    population: Population


class StopInput(EngineModel):
    category: Literal["stopper"]
    execution_id: UUID
    generation: int = Field(ge=0)
    population_size: int = Field(ge=0)
    best_individual_id: UUID | None = None
    best_total_score: float | None = None
    best_feasible: bool = False


class StopResult(EngineModel):
    category: Literal["stopper"]
    should_stop: bool
    reason: str | None = None


ComponentInputPayload = Annotated[
    SeedInput | ScoreInput | SelectInput | MutateInput | CullInput | StopInput,
    Field(discriminator="category"),
]

ComponentResultPayload = Annotated[
    SeedResult | ScoreResult | SelectResult | MutateResult | CullResult | StopResult,
    Field(discriminator="category"),
]
