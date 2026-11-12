"""Registry and runner: dispatch, validation, and error context."""

from __future__ import annotations

from uuid import UUID

import pytest

from scheduler_api.engine.components import CoverageScorer
from scheduler_api.engine.errors import (
    ComponentCategoryError,
    ComponentExecutionError,
    ComponentResultError,
    UnknownComponentError,
)
from scheduler_api.engine.execution.registry import ComponentRegistry
from scheduler_api.engine.execution.runner import ComponentRunner
from scheduler_api.engine.models.component_io import (
    CoverageScoreInput,
    CoverageScoreResult,
    ScoreResult,
    StopResult,
)
from scheduler_api.engine.models.config import CoverageScorerConfig
from scheduler_api.engine.models.phase import ComponentCategory, ComponentInvocation
from scheduler_api.engine.determinism import derive_uuid
from scheduler_api.tests.engine.builders import (
    WORKER_1,
    make_individual,
    make_problem,
    make_shift,
)


class UnknownIdScorer:
    """A scorer that reports on individuals it was never given."""

    component_id = "coverage"

    def score(self, input: CoverageScoreInput) -> ScoreResult:
        return CoverageScoreResult(scores={UUID(int=999): 10.0})


class RaisingScorer:
    component_id = "coverage"

    def score(self, input: CoverageScoreInput) -> ScoreResult:
        raise RuntimeError("boom")


class WrongResultScorer:
    """A scorer that returns a result belonging to a different category."""

    component_id = "coverage"

    def score(self, input: CoverageScoreInput) -> ScoreResult:
        return StopResult(should_stop=True, reason="wrong category")  # type: ignore[return-value]


class MisstatedComponent:
    component_id = "declared_elsewhere"

    def score(self, input: CoverageScoreInput) -> ScoreResult:
        return ScoreResult()


def invocation(problem, category=ComponentCategory.SCORER, component_id="coverage"):
    return ComponentInvocation(
        invocation_id=derive_uuid("inv", component_id),
        category=category,
        input=CoverageScoreInput(
            problem=problem,
            individuals=(
                make_individual((make_shift(WORKER_1, UUID(int=101), 8, 16),)),
            ),
            config=CoverageScorerConfig(),
        ),
    )


def test_default_registry_contains_every_mvp_component(registry) -> None:
    assert registry.component_ids() == frozenset(
        {
            "random_shifts",
            "coverage",
            "overstaffing",
            "skills_match",
            "shift_length",
            "availability",
            "double_booking",
            "schedule_limits",
            "select_top_n",
            "random_shift",
            "cull_top_n",
            "generation_count",
        }
    )


def test_registry_resolves_by_category() -> None:
    registry = ComponentRegistry()
    registry.register_scorer("coverage", CoverageScorer())
    assert isinstance(
        registry.resolve(ComponentCategory.SCORER, "coverage"), CoverageScorer
    )
    assert registry.components_in(ComponentCategory.SCORER) == frozenset({"coverage"})


def test_registry_rejects_duplicate_ids_across_categories() -> None:
    registry = ComponentRegistry()
    registry.register_scorer("coverage", CoverageScorer())

    class Imposter:
        component_id = "coverage"

        def select(self, input):  # pragma: no cover - never called
            raise AssertionError

    with pytest.raises(ComponentCategoryError):
        registry.register_selector("coverage", Imposter())


def test_registry_rejects_a_component_that_lies_about_its_id() -> None:
    registry = ComponentRegistry()
    with pytest.raises(ComponentCategoryError):
        registry.register_scorer("coverage", MisstatedComponent())


def test_registry_rejects_unknown_ids() -> None:
    registry = ComponentRegistry()
    with pytest.raises(UnknownComponentError):
        registry.resolve(ComponentCategory.SCORER, "nope")
    with pytest.raises(UnknownComponentError):
        registry.category_of("nope")


def test_registry_rejects_category_mismatch() -> None:
    registry = ComponentRegistry()
    registry.register_scorer("coverage", CoverageScorer())
    with pytest.raises(ComponentCategoryError):
        registry.resolve(ComponentCategory.MUTATOR, "coverage")


def test_runner_returns_an_envelope_matching_the_invocation(
    problem, registry, runner
) -> None:
    request = invocation(problem)
    result = runner.run(request)
    assert result.invocation_id == request.invocation_id
    assert result.category is ComponentCategory.SCORER
    assert isinstance(result.result, CoverageScoreResult)


def test_runner_rejects_scores_for_unknown_individuals(problem) -> None:
    registry = ComponentRegistry()
    registry.register_scorer("coverage", UnknownIdScorer())
    runner = ComponentRunner(registry)
    with pytest.raises(ComponentResultError):
        runner.run(invocation(problem))


def test_runner_wraps_component_failures_with_context(problem) -> None:
    registry = ComponentRegistry()
    registry.register_scorer("coverage", RaisingScorer())
    runner = ComponentRunner(registry)
    request = invocation(problem)
    with pytest.raises(ComponentExecutionError) as excinfo:
        runner.run(request)
    error = excinfo.value
    assert error.component_id == "coverage"
    assert error.invocation_id == request.invocation_id
    assert "boom" in str(error)


def test_runner_rejects_a_result_of_the_wrong_type(problem) -> None:
    registry = ComponentRegistry()
    registry.register_scorer("coverage", WrongResultScorer())
    runner = ComponentRunner(registry)
    with pytest.raises(ComponentResultError):
        runner.run(invocation(problem))


def test_score_results_reject_out_of_range_scores() -> None:
    with pytest.raises(ValueError):
        ScoreResult(scores={UUID(int=1): 150.0})


def test_invocation_input_must_match_its_config_id() -> None:
    from scheduler_api.engine.models.config import OverstaffingScorerConfig

    problem = make_problem()
    with pytest.raises(ValueError):
        CoverageScoreInput(
            problem=problem,
            individuals=(),
            config=OverstaffingScorerConfig(),
        )
