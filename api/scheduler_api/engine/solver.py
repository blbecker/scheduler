"""The concrete GA solver definition.

A solver is an orchestration object: it registers components and holds the
settings that describe the algorithm. It contains no execution logic and does not
know whether execution is local or distributed.
"""

from __future__ import annotations

from uuid import UUID

from scheduler_api.engine.components import (
    AvailabilityScorer,
    CoverageScorer,
    DoubleBookingScorer,
    GenerationCountStopper,
    OverstaffingScorer,
    RandomShiftMutator,
    RandomShiftSeeder,
    ScheduleLimitsScorer,
    ShiftLengthScorer,
    SkillsMatchScorer,
    TopNCuller,
    TopNSelector,
)
from scheduler_api.engine.execution.registry import ComponentRegistry
from scheduler_api.engine.models.config import (
    AvailabilityScorerConfig,
    CoverageScorerConfig,
    DoubleBookingScorerConfig,
    GenerationCountStopperConfig,
    OverstaffingScorerConfig,
    RandomShiftMutatorConfig,
    ScheduleLimitsScorerConfig,
    SeedRandomShiftsConfig,
    ShiftLengthScorerConfig,
    SkillsMatchScorerConfig,
    TopNCullerConfig,
    TopNSelectorConfig,
)
from scheduler_api.engine.models.execution import ExecutionRequest, SolverSettings
from scheduler_api.engine.models.fitness import FitnessConfig
from scheduler_api.engine.models.problem import SchedulingProblem

#: Scorers that only detect rule breaches carry weight 0: their violations make a
#: candidate infeasible, but their scores must not enter fitness.
CONSTRAINT_ONLY_COMPONENTS = ("availability", "double_booking", "schedule_limits")

DEFAULT_POPULATION_SIZE = 12
DEFAULT_PARENT_COUNT = 6
DEFAULT_OFFSPRING_COUNT = 12
DEFAULT_MAXIMUM_GENERATIONS = 10


def build_default_registry() -> ComponentRegistry:
    """Register the MVP component set."""
    registry = ComponentRegistry()
    registry.register_seeder("random_shifts", RandomShiftSeeder())
    registry.register_scorer("coverage", CoverageScorer())
    registry.register_scorer("overstaffing", OverstaffingScorer())
    registry.register_scorer("skills_match", SkillsMatchScorer())
    registry.register_scorer("shift_length", ShiftLengthScorer())
    registry.register_scorer("availability", AvailabilityScorer())
    registry.register_scorer("double_booking", DoubleBookingScorer())
    registry.register_scorer("schedule_limits", ScheduleLimitsScorer())
    registry.register_selector("select_top_n", TopNSelector())
    registry.register_mutator("random_shift", RandomShiftMutator())
    registry.register_culler("cull_top_n", TopNCuller())
    registry.register_stopper("generation_count", GenerationCountStopper())
    return registry


def default_solver_settings(
    *,
    population_size: int = DEFAULT_POPULATION_SIZE,
    parent_count: int = DEFAULT_PARENT_COUNT,
    offspring_count: int = DEFAULT_OFFSPRING_COUNT,
    maximum_generations: int = DEFAULT_MAXIMUM_GENERATIONS,
    max_candidates: int = 1,
    preserve_best: int = 1,
    fitness: FitnessConfig | None = None,
    mutation_rate_steps: int = 1,
) -> SolverSettings:
    """Equal weights across the quality scorers, zero for constraint-only ones."""
    resolved_fitness = fitness or FitnessConfig(
        weights={
            "coverage": 1.0,
            "overstaffing": 1.0,
            "skills_match": 1.0,
            "shift_length": 1.0,
            "availability": 0.0,
            "double_booking": 0.0,
            "schedule_limits": 0.0,
        }
    )
    return SolverSettings(
        population_size=population_size,
        parent_count=parent_count,
        offspring_count=offspring_count,
        max_candidates=max_candidates,
        preserve_best=preserve_best,
        fitness=resolved_fitness,
        seeders=(SeedRandomShiftsConfig(contribution=population_size),),
        scorers=(
            CoverageScorerConfig(),
            OverstaffingScorerConfig(),
            SkillsMatchScorerConfig(),
            ShiftLengthScorerConfig(),
            AvailabilityScorerConfig(),
            DoubleBookingScorerConfig(),
            ScheduleLimitsScorerConfig(),
        ),
        selector=TopNSelectorConfig(),
        mutators=(
            RandomShiftMutatorConfig(
                share=offspring_count,
                mutations_per_offspring=mutation_rate_steps,
            ),
        ),
        culler=TopNCullerConfig(),
        stoppers=(
            GenerationCountStopperConfig(maximum_generations=maximum_generations),
        ),
    )


class GeneticAlgorithmSolver:
    """A genetic algorithm expressed as components plus settings."""

    component_id = "genetic_algorithm"

    def __init__(
        self,
        registry: ComponentRegistry | None = None,
        settings: SolverSettings | None = None,
    ) -> None:
        self._registry = registry or build_default_registry()
        self._settings = settings or default_solver_settings()

    @property
    def registry(self) -> ComponentRegistry:
        return self._registry

    @property
    def settings(self) -> SolverSettings:
        return self._settings

    def build_request(
        self,
        *,
        execution_id: UUID,
        problem: SchedulingProblem,
        random_seed: int,
    ) -> ExecutionRequest:
        """Describe one execution of this solver."""
        if not self._settings.seeders:
            raise ValueError("the solver has no seeders")
        return ExecutionRequest(
            execution_id=execution_id,
            problem=problem,
            random_seed=random_seed,
            settings=self._settings,
        )
