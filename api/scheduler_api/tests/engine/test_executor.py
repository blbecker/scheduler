"""Local executor: end-to-end runs, determinism, and failure handling."""

from __future__ import annotations

from uuid import uuid4

import pytest

from scheduler_api.engine.errors import ComponentExecutionError, ExecutionStateError
from scheduler_api.engine.execution.local import LocalExecutor
from scheduler_api.engine.execution.registry import ComponentRegistry
from scheduler_api.engine.execution.runner import ComponentRunner
from scheduler_api.engine.execution.store import InMemoryExecutionStore
from scheduler_api.engine.models.config import CoverageScorerConfig
from scheduler_api.engine.models.execution import ExecutionStatus
from scheduler_api.engine.solver import (
    GeneticAlgorithmSolver,
    build_default_registry,
    default_solver_settings,
)
from scheduler_api.tests.engine.builders import make_problem


def run_once(*, seed=21, execution_id=None, settings=None):
    registry = build_default_registry()
    runner = ComponentRunner(registry)
    store = InMemoryExecutionStore()
    solver = GeneticAlgorithmSolver(
        registry=registry,
        settings=settings
        or default_solver_settings(
            population_size=4,
            parent_count=2,
            offspring_count=4,
            maximum_generations=2,
        ),
    )
    controller = __import__(
        "scheduler_api.engine.controller", fromlist=["GAController"]
    ).GAController(solver, runner, store)
    executor = LocalExecutor(controller, runner)
    resolved = execution_id or uuid4()
    store.save_request(
        solver.build_request(
            execution_id=resolved, problem=make_problem(), random_seed=seed
        )
    )
    executor.execute(resolved)
    return store, resolved


def test_executing_a_problem_produces_one_ranked_candidate() -> None:
    store, execution_id = run_once()
    result = store.load_result(execution_id)
    assert result is not None
    assert len(result.candidates) == 1
    candidate = result.candidates[0]
    assert candidate.rank == 1
    assert 0.0 <= candidate.fitness <= 100.0
    assert candidate.shifts
    assert result.termination_reason
    assert store.load_state(execution_id).status is ExecutionStatus.COMPLETED


def test_the_engine_produces_feasible_schedules_for_a_satisfiable_problem() -> None:
    store, execution_id = run_once()
    result = store.load_result(execution_id)
    assert result is not None
    assert result.candidates[0].feasible
    assert result.candidates[0].violations == ()


def test_the_same_request_and_seed_produce_an_identical_result() -> None:
    execution_id = uuid4()
    first_store, _ = run_once(execution_id=execution_id, seed=33)
    second_store, _ = run_once(execution_id=execution_id, seed=33)
    first = first_store.load_result(execution_id)
    second = second_store.load_result(execution_id)
    assert first is not None and second is not None
    assert first.model_dump_json() == second.model_dump_json()


def test_different_seeds_produce_different_executions() -> None:
    first_store, first_id = run_once(seed=33)
    second_store, second_id = run_once(seed=34)
    first = first_store.load_result(first_id)
    second = second_store.load_result(second_id)
    assert first is not None and second is not None
    assert first.random_seed != second.random_seed


def test_component_failure_fails_the_execution() -> None:
    class ExplodingScorer:
        component_id = "coverage"

        def score(self, input):
            raise RuntimeError("scorer exploded")

    registry = ComponentRegistry()
    registry.register_scorer("coverage", ExplodingScorer())
    registry.register_seeder(
        "random_shifts",
        __import__(
            "scheduler_api.engine.components", fromlist=["RandomShiftSeeder"]
        ).RandomShiftSeeder(),
    )
    registry.register_selector(
        "select_top_n",
        __import__(
            "scheduler_api.engine.components", fromlist=["TopNSelector"]
        ).TopNSelector(),
    )
    registry.register_mutator(
        "random_shift",
        __import__(
            "scheduler_api.engine.components", fromlist=["RandomShiftMutator"]
        ).RandomShiftMutator(),
    )
    registry.register_culler(
        "cull_top_n",
        __import__(
            "scheduler_api.engine.components", fromlist=["TopNCuller"]
        ).TopNCuller(),
    )
    registry.register_stopper(
        "generation_count",
        __import__(
            "scheduler_api.engine.components", fromlist=["GenerationCountStopper"]
        ).GenerationCountStopper(),
    )
    from scheduler_api.engine.models.execution import SolverSettings
    from scheduler_api.engine.models.fitness import FitnessConfig
    from scheduler_api.engine.models.config import (
        GenerationCountStopperConfig,
        RandomShiftMutatorConfig,
        SeedRandomShiftsConfig,
        TopNCullerConfig,
        TopNSelectorConfig,
    )

    settings = SolverSettings(
        population_size=2,
        parent_count=1,
        offspring_count=2,
        max_candidates=1,
        preserve_best=1,
        fitness=FitnessConfig(weights={"coverage": 1.0}),
        seeders=(SeedRandomShiftsConfig(contribution=2),),
        scorers=(CoverageScorerConfig(),),
        selector=TopNSelectorConfig(),
        mutators=(RandomShiftMutatorConfig(share=2),),
        culler=TopNCullerConfig(),
        stoppers=(GenerationCountStopperConfig(maximum_generations=1),),
    )
    runner = ComponentRunner(registry)
    store = InMemoryExecutionStore()
    solver = GeneticAlgorithmSolver(
        registry=registry,
        settings=settings,
    )
    from scheduler_api.engine.controller import GAController

    controller = GAController(solver, runner, store)
    executor = LocalExecutor(controller, runner)
    execution_id = uuid4()
    store.save_request(
        solver.build_request(
            execution_id=execution_id, problem=make_problem(), random_seed=1
        )
    )
    with pytest.raises(ComponentExecutionError):
        executor.execute(execution_id)
    state = store.load_state(execution_id)
    assert state.status is ExecutionStatus.FAILED
    assert state.failure_reason is not None
    assert "scorer exploded" in state.failure_reason
    with pytest.raises(ExecutionStateError):
        controller.result(execution_id)


def test_result_access_goes_through_the_store() -> None:
    store, execution_id = run_once()
    assert store.load_result(execution_id) is not None
    missing = uuid4()
    assert store.load_result(missing) is None
