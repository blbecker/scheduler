"""DTOs for solve components with type enums."""

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class ScorerType(str, Enum):
    """Available scorer types."""

    SKILLS_MATCH = "skills_match_scorer"


class MutatorType(str, Enum):
    """Available mutator types."""

    RANDOM_ASSIGNMENT = "random_assignment_mutator"
    SWAP_ASSIGNMENT = "swap_assignment_mutator"


class ConstraintType(str, Enum):
    """Available constraint types."""

    NO_DOUBLE_BOOKING = "no_double_booking_constraint"


class SelectorType(str, Enum):
    """Available selector types."""

    TOP_N = "top_n_selector"
    TOURNAMENT = "tournament_selector"
    RANKING = "ranking_selector"
    ROULETTE_WHEEL = "roulette_wheel_selector"


class SeederType(str, Enum):
    """Available seeder types."""

    RANDOM = "random_seeder"


class StopConditionType(str, Enum):
    """Available stop condition types."""

    GENERATION_LIMIT = "generation_limit_stop_condition"


class ScorerDTO(BaseModel):
    """DTO for scorer component."""

    component_type: ScorerType = Field(description="Type of scorer")
    name: str = Field(description="Human-readable name")
    config: dict[str, Any] = Field(
        default_factory=dict, description="Component configuration"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "component_type": "skills_match_scorer",
                "name": "Skills Match Scorer",
                "config": {},
            }
        }
    )


class MutatorDTO(BaseModel):
    """DTO for mutator component."""

    component_type: MutatorType = Field(description="Type of mutator")
    name: str = Field(description="Human-readable name")
    config: dict[str, Any] = Field(
        default_factory=dict, description="Component configuration"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "component_type": "random_assignment_mutator",
                "name": "Random Assignment Mutator",
                "config": {"mutation_rate": 0.1},
            }
        }
    )


class ConstraintDTO(BaseModel):
    """DTO for constraint component."""

    component_type: ConstraintType = Field(description="Type of constraint")
    name: str = Field(description="Human-readable name")
    config: dict[str, Any] = Field(
        default_factory=dict, description="Component configuration"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "component_type": "no_double_booking_constraint",
                "name": "No Double Booking Constraint",
                "config": {},
            }
        }
    )


class SelectorDTO(BaseModel):
    """DTO for selector component."""

    component_type: SelectorType = Field(description="Type of selector")
    name: str = Field(description="Human-readable name")
    config: dict[str, Any] = Field(
        default_factory=dict, description="Component configuration"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "component_type": "top_n_selector",
                "name": "Top N Selector",
                "config": {"top_n": 25},
            }
        }
    )


class SeederDTO(BaseModel):
    """DTO for seeder component."""

    component_type: SeederType = Field(description="Type of seeder")
    name: str = Field(description="Human-readable name")
    config: dict[str, Any] = Field(
        default_factory=dict, description="Component configuration"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "component_type": "random_seeder",
                "name": "Random Seeder",
                "config": {},
            }
        }
    )


class StopConditionDTO(BaseModel):
    """DTO for stop condition component."""

    component_type: StopConditionType = Field(description="Type of stop condition")
    name: str = Field(description="Human-readable name")
    config: dict[str, Any] = Field(
        default_factory=dict, description="Component configuration"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "component_type": "generation_limit_stop_condition",
                "name": "Generation Limit Stop Condition",
                "config": {"max_generations": 100},
            }
        }
    )


class SolvePhase(str, Enum):
    """Solve progress phase."""

    PENDING = "pending"
    PROGRESSING = "progressing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
