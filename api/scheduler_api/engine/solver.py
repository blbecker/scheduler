from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from scheduler_api.engine.components.cullers.top_n import TopNCuller
from scheduler_api.engine.components.mutators.random_replacement import (
    RandomReplacementMutator,
)
from scheduler_api.engine.components.scorers.coverage import CoverageScorer
from scheduler_api.engine.components.scorers.shift_length import (
    ShiftLengthScorer,
)
from scheduler_api.engine.components.scorers.skills_match import (
    SkillsMatchScorer,
)
from scheduler_api.engine.components.scorers.overlap import (
    WorkerOverlapScorer,
)
from scheduler_api.engine.components.seeders.random import (
    RandomScheduleSeeder,
)
from scheduler_api.engine.components.selectors.top_n import TopNSelector
from scheduler_api.engine.components.stoppers.generations import (
    GenerationCountStopper,
)
from scheduler_api.engine.exceptions import SolverConfigurationError
from scheduler_api.engine.execution.registry import ComponentRegistry
from scheduler_api.engine.models.component_config import (
    GenerationCountStopperConfig,
)
from scheduler_api.engine.models.phase import ComponentCategory
from scheduler_api.engine.models.problem import SchedulingProblem
from scheduler_api.engine.models.solver_spec import (
    MutatorPlan,
    SeederContribution,
    SolverSpec,
)
from scheduler_api.engine.models.scores import ScorerWeight, ScoringPolicy
from scheduler_api.engine.protocols import (
    Culler,
    Mutator,
    Scorer,
    Seeder,
    Selector,
    Stopper,
)

if TYPE_CHECKING:
    from scheduler_api.engine.controller import GeneticAlgorithmController


@dataclass(frozen=True)
class SeederBinding:
    component_id: str
    component: Seeder
    contribution: int


@dataclass(frozen=True)
class ScorerBinding:
    component_id: str
    component: Scorer
    weight: float


@dataclass(frozen=True)
class SelectorBinding:
    component_id: str
    component: Selector


@dataclass(frozen=True)
class MutatorBinding:
    component_id: str
    component: Mutator
    offspring_per_parent: int


@dataclass(frozen=True)
class CullerBinding:
    component_id: str
    component: Culler


@dataclass(frozen=True)
class StopperBinding:
    component_id: str
    component: Stopper


def _check_unique(component_ids: tuple[str, ...], category: str) -> None:
    seen: set[str] = set()
    for component_id in component_ids:
        if not component_id:
            raise SolverConfigurationError(f"{category} component ID must be non-empty")
        if component_id in seen:
            raise SolverConfigurationError(
                f"duplicate {category} component ID: {component_id}",
                component_id=component_id,
            )
        seen.add(component_id)


@dataclass(frozen=True)
class GeneticAlgorithmSolver:
    population_size: int
    random_seed: int
    seeders: tuple[SeederBinding, ...]
    scorers: tuple[ScorerBinding, ...]
    selector: SelectorBinding
    mutators: tuple[MutatorBinding, ...]
    culler: CullerBinding
    stoppers: tuple[StopperBinding, ...]
    elitism_count: int = 1

    def __post_init__(self) -> None:
        if self.population_size < 1:
            raise SolverConfigurationError("population_size must be >= 1")
        if self.random_seed < 0:
            raise SolverConfigurationError("random_seed must be >= 0")
        if not 0 <= self.elitism_count <= self.population_size:
            raise SolverConfigurationError(
                "elitism_count must be between 0 and population_size"
            )
        if not self.seeders:
            raise SolverConfigurationError("at least one seeder is required")
        if not self.scorers:
            raise SolverConfigurationError("at least one scorer is required")
        if not self.mutators:
            raise SolverConfigurationError("at least one mutator is required")
        if not self.stoppers:
            raise SolverConfigurationError("at least one stopper is required")

        if sum(binding.contribution for binding in self.seeders) != (
            self.population_size
        ):
            raise SolverConfigurationError(
                "seeder contributions must sum to population_size"
            )
        for binding in self.seeders:
            if binding.contribution < 1:
                raise SolverConfigurationError(
                    "seeder contribution must be >= 1",
                    component_id=binding.component_id,
                )
        for binding in self.mutators:
            if binding.offspring_per_parent < 1:
                raise SolverConfigurationError(
                    "offspring_per_parent must be >= 1",
                    component_id=binding.component_id,
                )
        for binding in self.scorers:
            if not 0.0 <= binding.weight <= 1.0:
                raise SolverConfigurationError(
                    "scorer weight must be between 0 and 1",
                    component_id=binding.component_id,
                )

        _check_unique(
            tuple(binding.component_id for binding in self.seeders),
            "seeder",
        )
        _check_unique((self.selector.component_id,), "selector")
        _check_unique(
            tuple(binding.component_id for binding in self.scorers),
            "scorer",
        )
        _check_unique(
            tuple(binding.component_id for binding in self.mutators),
            "mutator",
        )
        _check_unique((self.culler.component_id,), "culler")
        _check_unique(
            tuple(binding.component_id for binding in self.stoppers),
            "stopper",
        )

        bindings = (
            (ComponentCategory.SEEDER, self.seeders),
            (ComponentCategory.SCORER, self.scorers),
            (ComponentCategory.SELECTOR, (self.selector,)),
            (ComponentCategory.MUTATOR, self.mutators),
            (ComponentCategory.CULLER, (self.culler,)),
            (ComponentCategory.STOPPER, self.stoppers),
        )
        for category, category_bindings in bindings:
            for binding in category_bindings:
                if binding.component.component_category != category:
                    raise SolverConfigurationError(
                        f"component {binding.component_id} does not declare "
                        f"category {category.value}",
                        component_id=binding.component_id,
                    )

    def build_registry(self) -> ComponentRegistry:
        registry = ComponentRegistry()
        for binding in self.seeders:
            registry.register_seeder(binding.component_id, binding.component)
        for binding in self.scorers:
            registry.register_scorer(binding.component_id, binding.component)
        registry.register_selector(self.selector.component_id, self.selector.component)
        for binding in self.mutators:
            registry.register_mutator(binding.component_id, binding.component)
        registry.register_culler(self.culler.component_id, self.culler.component)
        for binding in self.stoppers:
            registry.register_stopper(binding.component_id, binding.component)
        return registry

    def to_spec(self) -> SolverSpec:
        return SolverSpec(
            population_size=self.population_size,
            random_seed=self.random_seed,
            elitism_count=self.elitism_count,
            seeders=tuple(
                SeederContribution(
                    component_id=binding.component_id,
                    contribution=binding.contribution,
                )
                for binding in self.seeders
            ),
            scorer_ids=tuple(binding.component_id for binding in self.scorers),
            scoring_policy=ScoringPolicy(
                weights=tuple(
                    ScorerWeight(
                        component_id=binding.component_id,
                        weight=binding.weight,
                    )
                    for binding in self.scorers
                )
            ),
            selector_id=self.selector.component_id,
            mutators=tuple(
                MutatorPlan(
                    component_id=binding.component_id,
                    offspring_per_parent=binding.offspring_per_parent,
                )
                for binding in self.mutators
            ),
            culler_id=self.culler.component_id,
            stopper_ids=tuple(binding.component_id for binding in self.stoppers),
        )

    def create_controller(
        self, problem: SchedulingProblem
    ) -> GeneticAlgorithmController:
        from scheduler_api.engine.controller import (
            GeneticAlgorithmController,
        )

        return GeneticAlgorithmController(self.to_spec(), problem)


def build_mvp_solver(
    *,
    population_size: int = 20,
    random_seed: int = 0,
    max_generations: int = 10,
    offspring_per_parent: int = 1,
    elitism_count: int = 1,
) -> GeneticAlgorithmSolver:
    return GeneticAlgorithmSolver(
        population_size=population_size,
        random_seed=random_seed,
        seeders=(
            SeederBinding(
                "random_schedule",
                RandomScheduleSeeder(),
                population_size,
            ),
        ),
        scorers=(
            ScorerBinding("skills_match", SkillsMatchScorer(), 0.0),
            ScorerBinding("worker_overlap", WorkerOverlapScorer(), 0.0),
            ScorerBinding("coverage", CoverageScorer(), 1.0),
            ScorerBinding("shift_length", ShiftLengthScorer(), 1.0),
        ),
        selector=SelectorBinding("top_n", TopNSelector()),
        mutators=(
            MutatorBinding(
                "random_replacement",
                RandomReplacementMutator(),
                offspring_per_parent,
            ),
        ),
        culler=CullerBinding("top_n", TopNCuller()),
        stoppers=(
            StopperBinding(
                "generation_count",
                GenerationCountStopper(
                    GenerationCountStopperConfig(max_generations=max_generations)
                ),
            ),
        ),
        elitism_count=elitism_count,
    )
