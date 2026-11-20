from __future__ import annotations

import math
from uuid import UUID

from pydantic import Field, field_validator

from .base import EngineModel
from .scores import Violation


class Assignment(EngineModel):
    worker_id: UUID
    job_id: UUID
    slot_index: int = Field(ge=0)


class Individual(EngineModel):
    id: UUID
    assignments: tuple[Assignment, ...]
    scores: dict[str, float] = Field(default_factory=dict)
    violations: tuple[Violation, ...] = ()

    @field_validator("assignments")
    @classmethod
    def _canonicalize_assignments(
        cls, value: tuple[Assignment, ...]
    ) -> tuple[Assignment, ...]:
        canonical = tuple(
            sorted(
                value,
                key=lambda assignment: (
                    assignment.slot_index,
                    assignment.job_id.hex,
                    assignment.worker_id.hex,
                ),
            )
        )
        if len(canonical) != len(set(canonical)):
            raise ValueError("individual contains duplicate assignments")
        return canonical

    @field_validator("scores")
    @classmethod
    def _validate_scores(cls, value: dict[str, float]) -> dict[str, float]:
        for component_id, score in value.items():
            if not component_id:
                raise ValueError("score keys must be non-empty")
            if not math.isfinite(score):
                raise ValueError("scores must be finite")
        return value

    @property
    def feasible(self) -> bool:
        return not self.violations
