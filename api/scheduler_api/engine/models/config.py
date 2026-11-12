"""Typed configuration for every component, supplied per execution.

Configuration travels inside the invocation input DTO, never on a component
instance: an invocation must be self-describing so a plan can be serialized,
replayed, and executed by a different process.
"""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field


class ComponentConfig(BaseModel):
    """Base for all component configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    component_id: str


# --- seeders ---------------------------------------------------------------


class SeedRandomShiftsConfig(ComponentConfig):
    component_id: Literal["random_shifts"] = "random_shifts"
    #: How many individuals this seeder contributes to the initial population.
    contribution: int = Field(ge=1)


SeederConfig = Annotated[SeedRandomShiftsConfig, Field(discriminator="component_id")]


# --- scorers ---------------------------------------------------------------


class CoverageScorerConfig(ComponentConfig):
    component_id: Literal["coverage"] = "coverage"


class OverstaffingScorerConfig(ComponentConfig):
    component_id: Literal["overstaffing"] = "overstaffing"


class SkillsMatchScorerConfig(ComponentConfig):
    component_id: Literal["skills_match"] = "skills_match"


class ShiftLengthScorerConfig(ComponentConfig):
    component_id: Literal["shift_length"] = "shift_length"


class AvailabilityScorerConfig(ComponentConfig):
    component_id: Literal["availability"] = "availability"


class DoubleBookingScorerConfig(ComponentConfig):
    component_id: Literal["double_booking"] = "double_booking"


class ScheduleLimitsScorerConfig(ComponentConfig):
    component_id: Literal["schedule_limits"] = "schedule_limits"


ScorerConfig = Annotated[
    Union[
        CoverageScorerConfig,
        OverstaffingScorerConfig,
        SkillsMatchScorerConfig,
        ShiftLengthScorerConfig,
        AvailabilityScorerConfig,
        DoubleBookingScorerConfig,
        ScheduleLimitsScorerConfig,
    ],
    Field(discriminator="component_id"),
]


# --- selector --------------------------------------------------------------


class TopNSelectorConfig(ComponentConfig):
    component_id: Literal["select_top_n"] = "select_top_n"


SelectorConfig = Annotated[TopNSelectorConfig, Field(discriminator="component_id")]


# --- mutators --------------------------------------------------------------


class RandomShiftMutatorConfig(ComponentConfig):
    component_id: Literal["random_shift"] = "random_shift"
    #: How many offspring this mutator contributes.
    share: int = Field(ge=1)
    #: How many mutation steps are applied to each offspring.
    mutations_per_offspring: int = Field(default=1, ge=1)
    weight_reassign_worker: float = Field(default=1.0, ge=0.0)
    weight_nudge_boundary: float = Field(default=1.0, ge=0.0)
    weight_delete_shift: float = Field(default=1.0, ge=0.0)
    weight_insert_shift: float = Field(default=1.0, ge=0.0)


MutatorConfig = Annotated[RandomShiftMutatorConfig, Field(discriminator="component_id")]


# --- culler ----------------------------------------------------------------


class TopNCullerConfig(ComponentConfig):
    component_id: Literal["cull_top_n"] = "cull_top_n"


CullerConfig = Annotated[TopNCullerConfig, Field(discriminator="component_id")]


# --- stopper ---------------------------------------------------------------


class GenerationCountStopperConfig(ComponentConfig):
    component_id: Literal["generation_count"] = "generation_count"
    maximum_generations: int = Field(ge=1)


StopperConfig = Annotated[
    GenerationCountStopperConfig, Field(discriminator="component_id")
]


#: Every config type the engine understands, as a single discriminated union.
AnyComponentConfig = Annotated[
    Union[
        SeedRandomShiftsConfig,
        CoverageScorerConfig,
        OverstaffingScorerConfig,
        SkillsMatchScorerConfig,
        ShiftLengthScorerConfig,
        AvailabilityScorerConfig,
        DoubleBookingScorerConfig,
        ScheduleLimitsScorerConfig,
        TopNSelectorConfig,
        RandomShiftMutatorConfig,
        TopNCullerConfig,
        GenerationCountStopperConfig,
    ],
    Field(discriminator="component_id"),
]
