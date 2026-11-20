from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import Field, field_validator

from .base import EngineModel


class ViolationCode(StrEnum):
    UNKNOWN_WORKER = "unknown_worker"
    UNKNOWN_JOB = "unknown_job"
    SLOT_OUT_OF_RANGE = "slot_out_of_range"
    UNQUALIFIED_WORKER = "unqualified_worker"
    UNAVAILABLE_WORKER = "unavailable_worker"
    WORKER_DOUBLE_BOOKED = "worker_double_booked"


class Violation(EngineModel):
    code: ViolationCode
    message: str
    worker_id: UUID | None = None
    job_id: UUID | None = None
    slot_index: int | None = None


class ScorerWeight(EngineModel):
    component_id: str = Field(min_length=1)
    weight: float = Field(ge=0.0)


class ScoringPolicy(EngineModel):
    weights: tuple[ScorerWeight, ...] = Field(min_length=1)

    @field_validator("weights")
    @classmethod
    def _unique_component_ids(
        cls, value: tuple[ScorerWeight, ...]
    ) -> tuple[ScorerWeight, ...]:
        component_ids = [weight.component_id for weight in value]
        if len(component_ids) != len(set(component_ids)):
            raise ValueError("scoring policy contains duplicate component IDs")
        return value

    def weight_for(self, component_id: str) -> float:
        for weight in self.weights:
            if weight.component_id == component_id:
                return weight.weight
        raise KeyError(component_id)
