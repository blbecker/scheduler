from __future__ import annotations

from pydantic import Field, field_validator, model_validator

from .base import EngineModel
from .scores import ScoringPolicy


class SeederContribution(EngineModel):
    component_id: str = Field(min_length=1)
    contribution: int = Field(ge=1)


class MutatorPlan(EngineModel):
    component_id: str = Field(min_length=1)
    offspring_per_parent: int = Field(ge=1)


class SolverSpec(EngineModel):
    population_size: int = Field(ge=1)
    random_seed: int = Field(ge=0)
    elitism_count: int = Field(ge=0)
    seeders: tuple[SeederContribution, ...] = Field(min_length=1)
    scorer_ids: tuple[str, ...] = Field(min_length=1)
    scoring_policy: ScoringPolicy
    selector_id: str = Field(min_length=1)
    mutators: tuple[MutatorPlan, ...] = Field(min_length=1)
    culler_id: str = Field(min_length=1)
    stopper_ids: tuple[str, ...] = Field(min_length=1)

    @field_validator("scorer_ids", "stopper_ids")
    @classmethod
    def _non_empty_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not component_id for component_id in value):
            raise ValueError("component IDs must be non-empty")
        return value

    @model_validator(mode="after")
    def _validate_spec(self) -> SolverSpec:
        contribution = sum(seeder.contribution for seeder in self.seeders)
        if contribution != self.population_size:
            raise ValueError("seeder contributions must sum to population_size")

        if self.elitism_count > self.population_size:
            raise ValueError("elitism_count must be <= population_size")

        seeder_ids = [seeder.component_id for seeder in self.seeders]
        mutator_ids = [mutator.component_id for mutator in self.mutators]
        for label, ids in (
            ("seeder", seeder_ids),
            ("scorer", list(self.scorer_ids)),
            ("mutator", mutator_ids),
            ("stopper", list(self.stopper_ids)),
        ):
            if len(ids) != len(set(ids)):
                raise ValueError(f"duplicate {label} component IDs")

        policy_ids = {weight.component_id for weight in self.scoring_policy.weights}
        if policy_ids != set(self.scorer_ids):
            raise ValueError("scorer_ids must match scoring policy component IDs")

        return self
