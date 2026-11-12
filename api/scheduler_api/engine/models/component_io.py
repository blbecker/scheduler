"""Per-component input and result DTOs, plus the invocation unions.

Every input DTO carries ``component_id`` as a ``Literal``, which is what makes
the unions discriminating. Adding a component means adding its DTOs to these
unions — deliberate friction that keeps serialization explicit.
"""

from __future__ import annotations

from typing import Annotated, Literal, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from scheduler_api.engine.models.config import (
    AvailabilityScorerConfig,
    CoverageScorerConfig,
    DoubleBookingScorerConfig,
    GenerationCountStopperConfig,
    OverstaffingScorerConfig,
    RandomShiftMutatorConfig,
    ScheduleLimitsScorerConfig,
    SeedRandomShiftsConfig,
    ShiftLengthScorerConfig,
    SkillsMatchScorerConfig,
    TopNCullerConfig,
    TopNSelectorConfig,
)
from scheduler_api.engine.models.genome import Individual, Population
from scheduler_api.engine.models.problem import SchedulingProblem
from scheduler_api.engine.models.scores import SCORE_MAX, SCORE_MIN, Violation


class ComponentInput(BaseModel):
    """Base for every component input."""

    model_config = ConfigDict(frozen=True)

    component_id: str

    @model_validator(mode="after")
    def _config_matches_id(self) -> "ComponentInput":
        config = getattr(self, "config", None)
        if (
            config is not None
            and getattr(config, "component_id", None) != self.component_id
        ):
            raise ValueError(
                "invocation component_id does not match its config component_id"
            )
        return self


class ComponentOutput(BaseModel):
    """Base for every component result."""

    model_config = ConfigDict(frozen=True)

    component_id: str


# --- seeder ----------------------------------------------------------------


class SeedRandomShiftsInput(ComponentInput):
    component_id: Literal["random_shifts"] = "random_shifts"
    problem: SchedulingProblem
    population_size: int = Field(ge=1)
    random_seed: int
    config: SeedRandomShiftsConfig


class SeedResult(ComponentOutput):
    component_id: Literal["random_shifts"] = "random_shifts"
    population: Population


# --- scorer ----------------------------------------------------------------


class ScoreInput(ComponentInput):
    """Input shared by every scorer."""

    problem: SchedulingProblem
    individuals: tuple[Individual, ...]


class ScoreResult(ComponentOutput):
    """Scores and violations for one scorer over one population."""

    scores: dict[UUID, float] = Field(default_factory=dict)
    violations: dict[UUID, tuple[Violation, ...]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_scores(self) -> "ScoreResult":
        for individual_id, score in self.scores.items():
            if not SCORE_MIN <= score <= SCORE_MAX:
                raise ValueError(
                    f"score for individual {individual_id} is outside [0, 100]"
                )
        return self


class CoverageScoreInput(ScoreInput):
    component_id: Literal["coverage"] = "coverage"
    config: CoverageScorerConfig


class OverstaffingScoreInput(ScoreInput):
    component_id: Literal["overstaffing"] = "overstaffing"
    config: OverstaffingScorerConfig


class SkillsMatchScoreInput(ScoreInput):
    component_id: Literal["skills_match"] = "skills_match"
    config: SkillsMatchScorerConfig


class ShiftLengthScoreInput(ScoreInput):
    component_id: Literal["shift_length"] = "shift_length"
    config: ShiftLengthScorerConfig


class AvailabilityScoreInput(ScoreInput):
    component_id: Literal["availability"] = "availability"
    config: AvailabilityScorerConfig


class DoubleBookingScoreInput(ScoreInput):
    component_id: Literal["double_booking"] = "double_booking"
    config: DoubleBookingScorerConfig


class ScheduleLimitsScoreInput(ScoreInput):
    component_id: Literal["schedule_limits"] = "schedule_limits"
    config: ScheduleLimitsScorerConfig


class CoverageScoreResult(ScoreResult):
    component_id: Literal["coverage"] = "coverage"


class OverstaffingScoreResult(ScoreResult):
    component_id: Literal["overstaffing"] = "overstaffing"


class SkillsMatchScoreResult(ScoreResult):
    component_id: Literal["skills_match"] = "skills_match"


class ShiftLengthScoreResult(ScoreResult):
    component_id: Literal["shift_length"] = "shift_length"


class AvailabilityScoreResult(ScoreResult):
    component_id: Literal["availability"] = "availability"


class DoubleBookingScoreResult(ScoreResult):
    component_id: Literal["double_booking"] = "double_booking"


class ScheduleLimitsScoreResult(ScoreResult):
    component_id: Literal["schedule_limits"] = "schedule_limits"


# --- selector --------------------------------------------------------------


class TopNSelectInput(ComponentInput):
    component_id: Literal["select_top_n"] = "select_top_n"
    individuals: tuple[Individual, ...]
    count: int = Field(ge=1)
    config: TopNSelectorConfig


class SelectResult(ComponentOutput):
    component_id: Literal["select_top_n"] = "select_top_n"
    individuals: tuple[Individual, ...]


# --- mutator ---------------------------------------------------------------


class RandomShiftMutateInput(ComponentInput):
    component_id: Literal["random_shift"] = "random_shift"
    problem: SchedulingProblem
    parents: tuple[Individual, ...]
    offspring_count: int = Field(ge=1)
    random_seed: int
    config: RandomShiftMutatorConfig


class MutateResult(ComponentOutput):
    component_id: Literal["random_shift"] = "random_shift"
    individuals: tuple[Individual, ...]


# --- culler ----------------------------------------------------------------


class TopNCullInput(ComponentInput):
    component_id: Literal["cull_top_n"] = "cull_top_n"
    candidates: tuple[Individual, ...]
    target_size: int = Field(ge=1)
    preserve_best: int = Field(default=0, ge=0)
    config: TopNCullerConfig


class CullResult(ComponentOutput):
    component_id: Literal["cull_top_n"] = "cull_top_n"
    population: Population


# --- stopper ---------------------------------------------------------------


class GenerationCountStopInput(ComponentInput):
    component_id: Literal["generation_count"] = "generation_count"
    generation: int = Field(ge=0)
    best_fitness: float | None = None
    best_feasible: bool = False
    population_size: int = Field(ge=1)
    config: GenerationCountStopperConfig


class StopResult(ComponentOutput):
    component_id: Literal["generation_count"] = "generation_count"
    should_stop: bool
    reason: str


# --- unions ----------------------------------------------------------------

ComponentInputUnion = Annotated[
    Union[
        SeedRandomShiftsInput,
        CoverageScoreInput,
        OverstaffingScoreInput,
        SkillsMatchScoreInput,
        ShiftLengthScoreInput,
        AvailabilityScoreInput,
        DoubleBookingScoreInput,
        ScheduleLimitsScoreInput,
        TopNSelectInput,
        RandomShiftMutateInput,
        TopNCullInput,
        GenerationCountStopInput,
    ],
    Field(discriminator="component_id"),
]

ComponentOutputUnion = Annotated[
    Union[
        SeedResult,
        CoverageScoreResult,
        OverstaffingScoreResult,
        SkillsMatchScoreResult,
        ShiftLengthScoreResult,
        AvailabilityScoreResult,
        DoubleBookingScoreResult,
        ScheduleLimitsScoreResult,
        SelectResult,
        MutateResult,
        CullResult,
        StopResult,
    ],
    Field(discriminator="component_id"),
]
