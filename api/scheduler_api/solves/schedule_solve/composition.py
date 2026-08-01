"""Schedule pipeline composition API for code-based configuration."""

from typing import Optional, Any
from .pipeline import ScheduleSolvePipeline
from scheduler_api.domain.schedule import Schedule
from .context import ScheduleSolveContext
from scheduler_api.engine.composition import (
    ChainOperator,
    ConditionalOperator,
    WeightedOperator,
)
from scheduler_api.engine.selection import (
    TournamentSelector,
    RouletteWheelSelector,
    RankingSelector,
)


class SchedulePipelineComposer:
    """Code-based composition API for schedule pipelines."""

    @staticmethod
    def compose_default() -> ScheduleSolvePipeline:
        """Compose default pipeline with enhanced operators."""
        from .seeders.random_seeder import RandomSeeder
        from .mutators.random_assignment_mutator import RandomAssignmentMutator
        from .mutators.swap_assignment_mutator import SwapAssignmentMutator
        from .scorers.skills_match_scorer import SkillsMatchScorer
        from .constraints.no_double_booking_constraint import NoDoubleBookingConstraint
        from scheduler_api.engine.stop_conditions.generation_limit import (
            GenerationLimitStopCondition,
        )

        # Create composed mutation pipeline
        mutation_pipeline = ChainOperator(
            [
                RandomAssignmentMutator(),
                ConditionalOperator(
                    condition=lambda g, ctx: len(g.get_assigned_workers()) > 2,
                    operator=SwapAssignmentMutator(),
                ),
            ]
        )

        # Create stop condition
        stop_condition = GenerationLimitStopCondition(max_generations=50)

        return ScheduleSolvePipeline(
            seeders=[RandomSeeder()],
            genome_operators=[mutation_pipeline],
            scorers=[SkillsMatchScorer()],
            constraints=[NoDoubleBookingConstraint()],
            selector=TournamentSelector(tournament_size=3),
            stop_conditions=[stop_condition],
        )

    @staticmethod
    def compose_advanced() -> ScheduleSolvePipeline:
        """Compose advanced pipeline with multiple strategies."""
        from .seeders.random_seeder import RandomSeeder
        from .mutators.random_assignment_mutator import RandomAssignmentMutator
        from .mutators.swap_assignment_mutator import SwapAssignmentMutator
        from .scorers.skills_match_scorer import SkillsMatchScorer
        from .constraints.no_double_booking_constraint import NoDoubleBookingConstraint
        from scheduler_api.engine.stop_conditions.generation_limit import (
            GenerationLimitStopCondition,
        )

        # Weighted mutation operators (70% random, 30% swap)
        weighted_mutators = WeightedOperator(
            [(RandomAssignmentMutator(), 0.7), (SwapAssignmentMutator(), 0.3)]
        )

        # Create stop condition
        stop_condition = GenerationLimitStopCondition(max_generations=100)

        return ScheduleSolvePipeline(
            seeders=[RandomSeeder()],
            genome_operators=[weighted_mutators],
            scorers=[SkillsMatchScorer()],
            constraints=[NoDoubleBookingConstraint()],
            selector=TournamentSelector(tournament_size=3),
            stop_conditions=[stop_condition],
        )

    @staticmethod
    def compose_performance() -> ScheduleSolvePipeline:
        """Compose performance-optimized pipeline."""
        from .seeders.random_seeder import RandomSeeder
        from .mutators.random_assignment_mutator import RandomAssignmentMutator
        from .mutators.swap_assignment_mutator import SwapAssignmentMutator
        from .scorers.skills_match_scorer import SkillsMatchScorer
        from .constraints.no_double_booking_constraint import NoDoubleBookingConstraint
        from scheduler_api.engine.stop_conditions.generation_limit import (
            GenerationLimitStopCondition,
        )

        # Conditional operators for different stages of evolution
        # We'll track generation in context parameters
        early_stage = ConditionalOperator(
            condition=lambda g, ctx: ctx.parameters.get("generation", 0) < 20,
            operator=RandomAssignmentMutator(),
            name="early_stage_mutation",
        )

        late_stage = ConditionalOperator(
            condition=lambda g, ctx: ctx.parameters.get("generation", 0) >= 20,
            operator=SwapAssignmentMutator(),
            name="late_stage_mutation",
        )

        # Use ranking selection for better diversity
        ranking_selector = RankingSelector(
            selection_pressure=1.7, ranking_method="linear", name="ranking_selector"
        )

        # Create stop condition
        stop_condition = GenerationLimitStopCondition(max_generations=150)

        return ScheduleSolvePipeline(
            seeders=[RandomSeeder()],
            genome_operators=[early_stage, late_stage],
            scorers=[SkillsMatchScorer()],
            constraints=[NoDoubleBookingConstraint()],
            selector=ranking_selector,
            stop_conditions=[stop_condition],
        )

    @staticmethod
    def compose_custom(
        seeders: list[Any],
        genome_operators: list[Any],
        scorers: list[Any],
        constraints: list[Any],
        selector: Any,
        stop_conditions: list[Any],
    ) -> ScheduleSolvePipeline:
        """Compose custom pipeline from provided components."""
        return ScheduleSolvePipeline(
            seeders=seeders,
            genome_operators=genome_operators,
            scorers=scorers,
            constraints=constraints,
            selector=selector,
            stop_conditions=stop_conditions,
        )

    @staticmethod
    def from_config(config: dict[str, Any]) -> ScheduleSolvePipeline:
        """Create pipeline from configuration dictionary."""
        # Import components based on config
        components = {}

        # TODO: Implement dynamic component loading from config
        # For now, use default
        return SchedulePipelineComposer.compose_default()
