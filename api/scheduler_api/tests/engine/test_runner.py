from __future__ import annotations

from uuid import UUID

import pytest

from scheduler_api.engine.exceptions import (
    ComponentCategoryMismatchError,
    ComponentExecutionError,
    EngineValidationError,
    InvalidComponentResultError,
)
from scheduler_api.engine.execution.registry import ComponentRegistry
from scheduler_api.engine.execution.runner import TypedComponentRunner
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
)
from scheduler_api.engine.models.population import Population
from scheduler_api.tests.engine.factories import make_policy, make_problem

EMPTY = Population(individuals=())
POLICY = make_policy()
COMPONENT_ID = "component"
INVOCATION_ID = UUID(int=1)


class FakeSeeder:
    component_category = ComponentCategory.SEEDER

    def __init__(self, result=None, error=None) -> None:
        self.result = result
        self.error = error
        self.received = None

    def seed(self, input: SeedInput):
        self.received = input
        if self.error is not None:
            raise self.error
        if self.result is not None:
            return self.result
        return SeedResult(category="seeder", population=EMPTY)


class FakeScorer:
    component_category = ComponentCategory.SCORER

    def score(self, input: ScoreInput):
        return ScoreResult(category="scorer", updates=())


class FakeSelector:
    component_category = ComponentCategory.SELECTOR

    def select(self, input: SelectInput):
        return SelectResult(category="selector", selected=EMPTY)


class FakeMutator:
    component_category = ComponentCategory.MUTATOR

    def mutate(self, input: MutateInput):
        return MutateResult(category="mutator", offspring=EMPTY)


class FakeCuller:
    component_category = ComponentCategory.CULLER

    def cull(self, input: CullInput):
        return CullResult(category="culler", population=EMPTY)


class FakeStopper:
    component_category = ComponentCategory.STOPPER

    def should_stop(self, input: StopInput):
        return StopResult(category="stopper", should_stop=False)


def make_invocation(category, payload) -> ComponentInvocation:
    return ComponentInvocation(
        invocation_id=INVOCATION_ID,
        component_id=COMPONENT_ID,
        category=category,
        input=payload,
    )


def make_input_payload(category: ComponentCategory):
    problem = make_problem()
    if category is ComponentCategory.SEEDER:
        return SeedInput(
            category="seeder",
            problem=problem,
            population_size=1,
            rng_seed=0,
        )
    if category is ComponentCategory.SCORER:
        return ScoreInput(category="scorer", problem=problem, population=EMPTY)
    if category is ComponentCategory.SELECTOR:
        return SelectInput(
            category="selector",
            population=EMPTY,
            count=0,
            scoring_policy=POLICY,
        )
    if category is ComponentCategory.MUTATOR:
        return MutateInput(
            category="mutator",
            problem=problem,
            parents=EMPTY,
            offspring_count=0,
            rng_seed=0,
        )
    if category is ComponentCategory.CULLER:
        return CullInput(
            category="culler",
            population=EMPTY,
            target_size=1,
            scoring_policy=POLICY,
        )
    return StopInput(
        category="stopper",
        execution_id=UUID(int=2),
        generation=0,
        population_size=0,
    )


@pytest.mark.parametrize(
    ("category", "component"),
    [
        (ComponentCategory.SEEDER, FakeSeeder()),
        (ComponentCategory.SCORER, FakeScorer()),
        (ComponentCategory.SELECTOR, FakeSelector()),
        (ComponentCategory.MUTATOR, FakeMutator()),
        (ComponentCategory.CULLER, FakeCuller()),
        (ComponentCategory.STOPPER, FakeStopper()),
    ],
)
def test_runner_dispatches_every_category(category, component):
    registry = ComponentRegistry()
    registry.register(category, COMPONENT_ID, component)
    runner = TypedComponentRunner(registry)
    invocation = make_invocation(category, make_input_payload(category))

    result = runner.run(invocation)

    assert result.invocation_id == INVOCATION_ID
    assert result.component_id == COMPONENT_ID
    assert result.category is category
    assert result.model_dump(mode="json")


def test_runner_rejects_wrong_input_model():
    registry = ComponentRegistry()
    registry.register(ComponentCategory.SEEDER, COMPONENT_ID, FakeSeeder())
    runner = TypedComponentRunner(registry)
    invocation = ComponentInvocation.model_construct(
        invocation_id=INVOCATION_ID,
        component_id=COMPONENT_ID,
        category=ComponentCategory.SEEDER,
        input=make_input_payload(ComponentCategory.SCORER),
    )

    with pytest.raises(ComponentCategoryMismatchError) as exc_info:
        runner.run(invocation)

    assert exc_info.value.component_id == COMPONENT_ID
    assert exc_info.value.invocation_id == INVOCATION_ID


def test_runner_wraps_component_exceptions():
    registry = ComponentRegistry()
    registry.register(
        ComponentCategory.SEEDER,
        COMPONENT_ID,
        FakeSeeder(error=RuntimeError("boom")),
    )
    runner = TypedComponentRunner(registry)
    invocation = make_invocation(
        ComponentCategory.SEEDER,
        make_input_payload(ComponentCategory.SEEDER),
    )

    with pytest.raises(ComponentExecutionError) as exc_info:
        runner.run(invocation)

    assert exc_info.value.component_id == COMPONENT_ID
    assert exc_info.value.invocation_id == INVOCATION_ID
    assert isinstance(exc_info.value.__cause__, RuntimeError)


def test_runner_preserves_engine_errors_with_context():
    engine_error = EngineValidationError("invalid")
    registry = ComponentRegistry()
    registry.register(
        ComponentCategory.SEEDER,
        COMPONENT_ID,
        FakeSeeder(error=engine_error),
    )
    runner = TypedComponentRunner(registry)
    invocation = make_invocation(
        ComponentCategory.SEEDER,
        make_input_payload(ComponentCategory.SEEDER),
    )

    with pytest.raises(EngineValidationError) as exc_info:
        runner.run(invocation)

    assert exc_info.value is engine_error
    assert exc_info.value.component_id == COMPONENT_ID
    assert exc_info.value.invocation_id == INVOCATION_ID


def test_runner_rejects_wrong_result_model():
    registry = ComponentRegistry()
    registry.register(
        ComponentCategory.SEEDER,
        COMPONENT_ID,
        FakeSeeder(result=ScoreResult(category="scorer", updates=())),
    )
    runner = TypedComponentRunner(registry)
    invocation = make_invocation(
        ComponentCategory.SEEDER,
        make_input_payload(ComponentCategory.SEEDER),
    )

    with pytest.raises(InvalidComponentResultError):
        runner.run(invocation)
