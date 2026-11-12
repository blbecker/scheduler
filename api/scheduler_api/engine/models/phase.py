"""Phase plans and results: the controller/executor boundary."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from scheduler_api.engine.models.component_io import (
    ComponentInputUnion,
    ComponentOutputUnion,
)


class PhaseType(StrEnum):
    SEED = "seed"
    SCORE = "score"
    SELECT = "select"
    MUTATE = "mutate"
    CULL = "cull"
    CHECK_STOP = "check_stop"


class ComponentCategory(StrEnum):
    SEEDER = "seeder"
    SCORER = "scorer"
    SELECTOR = "selector"
    MUTATOR = "mutator"
    CULLER = "culler"
    STOPPER = "stopper"


class ComponentInvocation(BaseModel):
    """One planned component call. Contains no Python objects, only DTOs."""

    model_config = ConfigDict(frozen=True)

    invocation_id: UUID
    category: ComponentCategory
    input: ComponentInputUnion


class PhasePlan(BaseModel):
    """One phase of work, fully self-describing."""

    model_config = ConfigDict(frozen=True)

    execution_id: UUID
    phase_execution_id: UUID
    generation: int = Field(ge=0)
    phase: PhaseType
    invocations: tuple[ComponentInvocation, ...] = ()


class ComponentResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    invocation_id: UUID
    category: ComponentCategory
    result: ComponentOutputUnion


class PhaseResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    execution_id: UUID
    phase_execution_id: UUID
    results: tuple[ComponentResult, ...] = ()
