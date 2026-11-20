from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import Field, model_validator

from .base import EngineModel
from .component_io import ComponentInputPayload, ComponentResultPayload


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


PHASE_CATEGORY: dict[PhaseType, ComponentCategory] = {
    PhaseType.SEED: ComponentCategory.SEEDER,
    PhaseType.SCORE: ComponentCategory.SCORER,
    PhaseType.SELECT: ComponentCategory.SELECTOR,
    PhaseType.MUTATE: ComponentCategory.MUTATOR,
    PhaseType.CULL: ComponentCategory.CULLER,
    PhaseType.CHECK_STOP: ComponentCategory.STOPPER,
}


class ComponentInvocation(EngineModel):
    invocation_id: UUID
    component_id: str = Field(min_length=1)
    category: ComponentCategory
    input: ComponentInputPayload

    @model_validator(mode="after")
    def _category_matches_input(self) -> ComponentInvocation:
        if ComponentCategory(self.input.category) != self.category:
            raise ValueError("invocation category does not match input payload")
        return self


class ComponentResult(EngineModel):
    invocation_id: UUID
    component_id: str = Field(min_length=1)
    category: ComponentCategory
    result: ComponentResultPayload

    @model_validator(mode="after")
    def _category_matches_result(self) -> ComponentResult:
        if ComponentCategory(self.result.category) != self.category:
            raise ValueError("result category does not match result payload")
        return self


class PhasePlan(EngineModel):
    execution_id: UUID
    phase_execution_id: UUID
    generation: int = Field(ge=0)
    phase: PhaseType
    invocations: tuple[ComponentInvocation, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_invocations(self) -> PhasePlan:
        invocation_ids = [invocation.invocation_id for invocation in self.invocations]
        if len(invocation_ids) != len(set(invocation_ids)):
            raise ValueError("phase plan contains duplicate invocation IDs")
        expected = PHASE_CATEGORY[self.phase]
        for invocation in self.invocations:
            if invocation.category != expected:
                raise ValueError("invocation category does not match phase category")
        return self


class PhaseResult(EngineModel):
    execution_id: UUID
    phase_execution_id: UUID
    results: tuple[ComponentResult, ...] = Field(min_length=1)
