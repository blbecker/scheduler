from __future__ import annotations

from pydantic import Field

from .base import EngineModel


class RandomScheduleSeederConfig(EngineModel):
    shuffle_demand_order: bool = True


class SkillsMatchScorerConfig(EngineModel):
    check_availability: bool = True


class CoverageScorerConfig(EngineModel):
    overstaffing_weight: float = Field(default=1.0, ge=0.0)


class ShiftLengthScorerConfig(EngineModel):
    under_minimum_weight: float = Field(default=1.0, ge=0.0)
    over_maximum_weight: float = Field(default=1.0, ge=0.0)


class RandomReplacementMutatorConfig(EngineModel):
    replacements_per_offspring: int = Field(default=1, ge=1)


class GenerationCountStopperConfig(EngineModel):
    max_generations: int = Field(default=10, ge=1)
