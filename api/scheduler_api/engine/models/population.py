from __future__ import annotations

from pydantic import field_validator

from .assignment import Individual
from .base import EngineModel


class Population(EngineModel):
    individuals: tuple[Individual, ...]

    @field_validator("individuals")
    @classmethod
    def _unique_individual_ids(
        cls, value: tuple[Individual, ...]
    ) -> tuple[Individual, ...]:
        individual_ids = [individual.id for individual in value]
        if len(individual_ids) != len(set(individual_ids)):
            raise ValueError("population contains duplicate individual IDs")
        return value
