"""Fitness aggregation.

Scores are 0-100 per scorer; fitness is their weighted mean, so it stays on the
same 0-100 scale no matter how many scorers are configured. A weight of zero
excludes a scorer from fitness while keeping its violations.
"""

from __future__ import annotations

import math
from typing import Mapping

from pydantic import BaseModel, ConfigDict, Field, model_validator

from scheduler_api.engine.errors import ComponentResultError
from scheduler_api.engine.models.scores import SCORE_MAX, SCORE_MIN


class FitnessConfig(BaseModel):
    """Per-scorer weights, keyed by component id. Missing means 1.0."""

    model_config = ConfigDict(frozen=True)

    weights: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate(self) -> "FitnessConfig":
        for component_id, weight in self.weights.items():
            if not math.isfinite(weight):
                raise ValueError(
                    f"weight for component {component_id!r} must be finite"
                )
            if weight < 0:
                raise ValueError(
                    f"weight for component {component_id!r} must not be negative"
                )
        return self

    def weight_for(self, component_id: str) -> float:
        return self.weights.get(component_id, 1.0)


def compute_fitness(scores: Mapping[str, float], config: FitnessConfig) -> float:
    """Weighted mean of the scored components, on a 0-100 scale."""
    weighted_total = 0.0
    total_weight = 0.0
    for component_id, score in scores.items():
        weight = config.weight_for(component_id)
        if weight <= 0:
            continue
        if not SCORE_MIN <= score <= SCORE_MAX:
            raise ComponentResultError(
                f"score for component {component_id!r} is outside [0, 100]: {score}"
            )
        weighted_total += weight * score
        total_weight += weight
    if total_weight <= 0:
        raise ComponentResultError(
            "no weighted scores were produced for the individual"
        )
    return weighted_total / total_weight
