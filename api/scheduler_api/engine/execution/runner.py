"""Typed component dispatch.

The runner is the one place that knows how an invocation maps to a component
method. It validates the input, calls the component, validates the result, and
returns a serializable envelope. It knows nothing about Celery.
"""

from __future__ import annotations

from typing import cast

from scheduler_api.engine.errors import (
    ComponentCategoryError,
    ComponentExecutionError,
    ComponentResultError,
    EngineError,
)
from scheduler_api.engine.execution.registry import (
    as_culler,
    as_mutator,
    as_scorer,
    as_seeder,
    as_selector,
    as_stopper,
)
from scheduler_api.engine.execution.registry import ComponentRegistry
from scheduler_api.engine.models.component_io import (
    ComponentOutput,
    ComponentOutputUnion,
    CullResult,
    GenerationCountStopInput,
    MutateResult,
    RandomShiftMutateInput,
    ScoreInput,
    ScoreResult,
    SeedRandomShiftsInput,
    SeedResult,
    SelectResult,
    StopResult,
    TopNCullInput,
    TopNSelectInput,
)
from scheduler_api.engine.models.phase import (
    ComponentCategory,
    ComponentInvocation,
    ComponentResult,
)

_EXPECTED_RESULT: dict[ComponentCategory, type[ComponentOutput]] = {
    ComponentCategory.SEEDER: SeedResult,
    ComponentCategory.SCORER: ScoreResult,
    ComponentCategory.SELECTOR: SelectResult,
    ComponentCategory.MUTATOR: MutateResult,
    ComponentCategory.CULLER: CullResult,
    ComponentCategory.STOPPER: StopResult,
}


class ComponentRunner:
    """Invokes one component by stable id."""

    def __init__(self, registry: ComponentRegistry) -> None:
        self._registry = registry

    def run(self, invocation: ComponentInvocation) -> ComponentResult:
        component = self._registry.resolve(
            invocation.category, invocation.input.component_id
        )
        try:
            result = self._dispatch(invocation, component)
        except EngineError:
            raise
        except Exception as exc:  # noqa: BLE001 - re-raised with context
            raise ComponentExecutionError(
                f"component raised {type(exc).__name__}: {exc}",
                component_id=invocation.input.component_id,
                invocation_id=invocation.invocation_id,
            ) from exc
        self._validate_result(invocation, result)
        return ComponentResult(
            invocation_id=invocation.invocation_id,
            category=invocation.category,
            result=cast(ComponentOutputUnion, result),
        )

    def _dispatch(
        self, invocation: ComponentInvocation, component: object
    ) -> ComponentOutput:
        match invocation.category:
            case ComponentCategory.SEEDER:
                return as_seeder(component).seed(
                    cast(SeedRandomShiftsInput, invocation.input)
                )
            case ComponentCategory.SCORER:
                return as_scorer(component).score(cast(ScoreInput, invocation.input))
            case ComponentCategory.SELECTOR:
                return as_selector(component).select(
                    cast(TopNSelectInput, invocation.input)
                )
            case ComponentCategory.MUTATOR:
                return as_mutator(component).mutate(
                    cast(RandomShiftMutateInput, invocation.input)
                )
            case ComponentCategory.CULLER:
                return as_culler(component).cull(cast(TopNCullInput, invocation.input))
            case ComponentCategory.STOPPER:
                return as_stopper(component).should_stop(
                    cast(GenerationCountStopInput, invocation.input)
                )
        raise ComponentCategoryError(
            f"unsupported component category {invocation.category!r}"
        )

    def _validate_result(
        self, invocation: ComponentInvocation, result: ComponentOutput
    ) -> None:
        expected = _EXPECTED_RESULT[invocation.category]
        if not isinstance(result, expected):
            raise ComponentResultError(
                f"component {invocation.input.component_id!r} returned "
                f"{type(result).__name__}, expected {expected.__name__}"
            )
        if result.component_id != invocation.input.component_id:
            raise ComponentResultError(
                f"result declares component_id {result.component_id!r} but the invocation "
                f"named {invocation.input.component_id!r}"
            )
        if isinstance(result, ScoreResult):
            self._validate_score_result(cast(ScoreInput, invocation.input), result)

    def _validate_score_result(
        self, score_input: ScoreInput, result: ScoreResult
    ) -> None:
        known = {individual.id for individual in score_input.individuals}
        unknown_scores = set(result.scores) - known
        if unknown_scores:
            raise ComponentResultError(
                f"{self._name(result)} scored unknown individuals "
                f"{sorted(map(str, unknown_scores))}"
            )
        unknown_violations = set(result.violations) - known
        if unknown_violations:
            raise ComponentResultError(
                f"{self._name(result)} reported violations for unknown individuals "
                f"{sorted(map(str, unknown_violations))}"
            )

    @staticmethod
    def _name(result: ComponentOutput) -> str:
        return f"component {result.component_id!r}"
