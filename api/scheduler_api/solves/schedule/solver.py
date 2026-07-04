"""Schedule solver implementation."""

from typing import Dict, List
from uuid import UUID
from ..interfaces import Solvable
from .context import ScheduleSolveContext
from .genome import ScheduleGenome
from .pipeline import ScheduleSolvePipeline


class ScheduleSolver(
    Solvable[
        ScheduleSolveContext,
        ScheduleGenome,
        List[ScheduleGenome],
        ScheduleSolvePipeline,
    ]
):
    """Solver for schedule optimization problems."""

    name: str = "schedule-solve"

    # Default parameters for testing with small genomes
    DEFAULT_PARAMETERS = {
        "population_size": 10,  # Small for testing
        "max_generations": 20,  # Quick runs
        "mutation_rate": 0.1,  # 10% mutation chance
        "selection_top_n": 5,  # Keep top 50%
        "elite_size": 1,  # Keep 1 elite
    }

    # For even smaller debugging
    DEBUG_PARAMETERS = {
        "population_size": 5,  # Very small
        "max_generations": 10,  # Very quick
        "mutation_rate": 0.2,  # Higher mutation for exploration
        "selection_top_n": 3,  # Keep top 60%
        "elite_size": 1,
    }

    def create_context(
        self, template_id: UUID, parameters: dict
    ) -> ScheduleSolveContext:
        """Create solve context from template and parameters."""
        # TODO: Load actual data from repositories
        # For now, create a mock context for testing
        from uuid import uuid4

        # Merge provided parameters with defaults
        merged_params = self.DEFAULT_PARAMETERS.copy()
        merged_params.update(parameters)

        # Create mock data for testing
        worker_ids = [uuid4() for _ in range(3)]  # 3 workers
        shift_ids = [uuid4() for _ in range(5)]  # 5 shifts

        # Mock skill IDs
        skill_a = uuid4()
        skill_b = uuid4()

        # Create context with mock data
        context = ScheduleSolveContext(
            template_id=template_id,
            worker_ids=worker_ids,
            shift_ids=shift_ids,
            skill_requirements={
                shift_ids[0]: [skill_a],  # 1 skill required
                shift_ids[1]: [skill_a, skill_b],  # 2 skills required
                shift_ids[2]: [skill_a],  # 1 skill required
                shift_ids[3]: [],  # No skills required
                shift_ids[4]: [skill_b],  # 1 skill required
            },
            worker_skills={
                worker_ids[0]: [skill_a, skill_b],  # Has both skills
                worker_ids[1]: [skill_a],  # Has skill_a only
                worker_ids[2]: [skill_b],  # Has skill_b only
            },
            parameters=merged_params,
        )

        return context

    def create_initial_population(
        self, context: ScheduleSolveContext, size: int
    ) -> List[ScheduleGenome]:
        """Generate initial population of genomes using configured seeder."""
        # Get the pipeline to access the seeder
        pipeline = self.create_pipeline()

        if not pipeline.seeders:
            raise ValueError("No seeder configured in pipeline")

        # Use the first seeder to generate initial population
        seeder = pipeline.seeders[0]
        return seeder.seed(context, size)

    def create_pipeline(self) -> ScheduleSolvePipeline:
        """Return pipeline configuration with component lists."""
        # Import here to avoid circular imports
        from .seeders.random_seeder import RandomSeeder
        from .mutators.random_assignment_mutator import RandomAssignmentMutator
        from .scorers.skills_match_scorer import SkillsMatchScorer
        from .constraints.no_double_booking_constraint import NoDoubleBookingConstraint
        from .selectors.top_n_selector import TopNSelector
        from ..engine.stop_conditions.generation_limit import (
            GenerationLimitStopCondition,
        )

        return ScheduleSolvePipeline(
            seeders=[RandomSeeder()],
            genome_operators=[RandomAssignmentMutator()],
            scorers=[SkillsMatchScorer()],
            constraints=[NoDoubleBookingConstraint()],
            selector=TopNSelector(),
            stop_conditions=[
                GenerationLimitStopCondition(
                    max_generations=self.DEFAULT_PARAMETERS["max_generations"]
                )
            ],
        )
