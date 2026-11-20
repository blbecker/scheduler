from __future__ import annotations

from typing import TypeVar

from scheduler_api.engine.exceptions import (
    ComponentCategoryMismatchError,
    ComponentExecutionError,
    EngineError,
    InvalidComponentResultError,
)
from scheduler_api.engine.execution.registry import ComponentRegistry
from scheduler_api.engine.models.component_io import (
    CullInput,
    CullResult,
    MutateInput,
    MutateResult,
    ScoreInput,
    ScoreResult,
    SeedInput,
    SeedResult,
    SelectInput,
    SelectResult,
    StopInput,
    StopResult,
)
from scheduler_api.engine.models.phase import (
    ComponentCategory,
    ComponentInvocation,
    ComponentResult,
    ComponentResultPayload,
)

PayloadT = TypeVar("PayloadT")


class TypedComponentRunner:
    """Resolve one invocation and call the matching component method."""

    def __init__(self, registry: ComponentRegistry) -> None:
        self._registry = registry

    def run(self, invocation: ComponentInvocation) -> ComponentResult:
        try:
            match invocation.category:
                case ComponentCategory.SEEDER:
                    component = self._registry.resolve_seeder(invocation.component_id)
                    payload = self._require_input(
                        invocation.input, SeedInput, invocation
                    )
                    result = component.seed(payload)
                    self._require_result(result, SeedResult, invocation)
                    return self._envelope(invocation, result)
                case ComponentCategory.SCORER:
                    component = self._registry.resolve_scorer(invocation.component_id)
                    payload = self._require_input(
                        invocation.input, ScoreInput, invocation
                    )
                    result = component.score(payload)
                    self._require_result(result, ScoreResult, invocation)
                    return self._envelope(invocation, result)
                case ComponentCategory.SELECTOR:
                    component = self._registry.resolve_selector(invocation.component_id)
                    payload = self._require_input(
                        invocation.input, SelectInput, invocation
                    )
                    result = component.select(payload)
                    self._require_result(result, SelectResult, invocation)
                    return self._envelope(invocation, result)
                case ComponentCategory.MUTATOR:
                    component = self._registry.resolve_mutator(invocation.component_id)
                    payload = self._require_input(
                        invocation.input, MutateInput, invocation
                    )
                    result = component.mutate(payload)
                    self._require_result(result, MutateResult, invocation)
                    return self._envelope(invocation, result)
                case ComponentCategory.CULLER:
                    component = self._registry.resolve_culler(invocation.component_id)
                    payload = self._require_input(
                        invocation.input, CullInput, invocation
                    )
                    result = component.cull(payload)
                    self._require_result(result, CullResult, invocation)
                    return self._envelope(invocation, result)
                case ComponentCategory.STOPPER:
                    component = self._registry.resolve_stopper(invocation.component_id)
                    payload = self._require_input(
                        invocation.input, StopInput, invocation
                    )
                    result = component.should_stop(payload)
                    self._require_result(result, StopResult, invocation)
                    return self._envelope(invocation, result)
        except EngineError as exc:
            if exc.component_id is None:
                exc.component_id = invocation.component_id
            if exc.invocation_id is None:
                exc.invocation_id = invocation.invocation_id
            raise
        except Exception as exc:
            raise ComponentExecutionError(
                f"component {invocation.component_id} failed: {exc}",
                component_id=invocation.component_id,
                invocation_id=invocation.invocation_id,
            ) from exc

    @staticmethod
    def _require_input(
        payload: object,
        expected: type[PayloadT],
        invocation: ComponentInvocation,
    ) -> PayloadT:
        if not isinstance(payload, expected):
            raise ComponentCategoryMismatchError(
                f"invocation for {invocation.component_id} carries "
                f"{type(payload).__name__}, expected {expected.__name__}",
                component_id=invocation.component_id,
                invocation_id=invocation.invocation_id,
            )
        return payload

    @staticmethod
    def _require_result(
        result: object,
        expected: type[PayloadT],
        invocation: ComponentInvocation,
    ) -> None:
        if not isinstance(result, expected):
            raise InvalidComponentResultError(
                f"component {invocation.component_id} returned "
                f"{type(result).__name__}, expected {expected.__name__}",
                component_id=invocation.component_id,
                invocation_id=invocation.invocation_id,
            )

    @staticmethod
    def _envelope(
        invocation: ComponentInvocation,
        result: ComponentResultPayload,
    ) -> ComponentResult:
        return ComponentResult(
            invocation_id=invocation.invocation_id,
            component_id=invocation.component_id,
            category=invocation.category,
            result=result,
        )
