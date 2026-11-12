"""Shared engine test fixtures."""

from __future__ import annotations

from uuid import uuid4

import pytest

from scheduler_api.engine.components import (
    CoverageScorer,
    GenerationCountStopper,
    RandomShiftMutator,
    RandomShiftSeeder,
    TopNCuller,
    TopNSelector,
)
from scheduler_api.engine.controller import GAController
from scheduler_api.engine.execution.local import LocalExecutor
from scheduler_api.engine.execution.registry import ComponentRegistry
from scheduler_api.engine.execution.runner import ComponentRunner
from scheduler_api.engine.execution.store import InMemoryExecutionStore
from scheduler_api.engine.models.execution import ExecutionRequest, SolverSettings
from scheduler_api.engine.models.fitness import FitnessConfig
from scheduler_api.engine.models.config import (
    CoverageScorerConfig,
    GenerationCountStopperConfig,
    RandomShiftMutatorConfig,
    SeedRandomShiftsConfig,
    TopNCullerConfig,
    TopNSelectorConfig,
)
from scheduler_api.engine.models.problem import SchedulingProblem
from scheduler_api.engine.solver import GeneticAlgorithmSolver, build_default_registry
from scheduler_api.tests.engine.builders import make_problem


@pytest.fixture
def problem() -> SchedulingProblem:
    return make_problem()


@pytest.fixture
def registry() -> ComponentRegistry:
    return build_default_registry()


@pytest.fixture
def runner(registry: ComponentRegistry) -> ComponentRunner:
    return ComponentRunner(registry)


@pytest.fixture
def store() -> InMemoryExecutionStore:
    return InMemoryExecutionStore()


def minimal_settings(
    *,
    population_size: int = 4,
    parent_count: int = 2,
    offspring_count: int = 4,
    maximum_generations: int = 1,
    max_candidates: int = 1,
    fitness: FitnessConfig | None = None,
) -> SolverSettings:
    """A small settings object using only the coverage scorer."""
    return SolverSettings(
        population_size=population_size,
        parent_count=parent_count,
        offspring_count=offspring_count,
        max_candidates=max_candidates,
        preserve_best=1,
        fitness=fitness or FitnessConfig(weights={"coverage": 1.0}),
        seeders=(SeedRandomShiftsConfig(contribution=population_size),),
        scorers=(CoverageScorerConfig(),),
        selector=TopNSelectorConfig(),
        mutators=(RandomShiftMutatorConfig(share=offspring_count),),
        culler=TopNCullerConfig(),
        stoppers=(
            GenerationCountStopperConfig(maximum_generations=maximum_generations),
        ),
    )


@pytest.fixture
def make_controller():
    """Build a controller/executor/store triple around a problem and settings."""

    def factory(
        problem: SchedulingProblem,
        *,
        settings: SolverSettings | None = None,
        seed: int = 7,
        registry: ComponentRegistry | None = None,
        execution_id=None,
    ):
        resolved_registry = registry or build_default_registry()
        runner = ComponentRunner(resolved_registry)
        execution_store = InMemoryExecutionStore()
        solver = GeneticAlgorithmSolver(
            registry=resolved_registry,
            settings=settings or minimal_settings(),
        )
        controller = GAController(solver, runner, execution_store)
        executor = LocalExecutor(controller, runner)
        resolved_id = execution_id or uuid4()
        request = solver.build_request(
            execution_id=resolved_id, problem=problem, random_seed=seed
        )
        execution_store.save_request(request)
        return controller, executor, execution_store, resolved_id

    return factory


__all__ = [
    "CoverageScorer",
    "ExecutionRequest",
    "GenerationCountStopper",
    "RandomShiftMutator",
    "RandomShiftSeeder",
    "TopNCuller",
    "TopNSelector",
    "minimal_settings",
]
