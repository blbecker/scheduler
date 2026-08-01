"""Schedule solver implementation."""

from uuid import UUID
from typing import Optional
from scheduler_api.engine.interfaces import Solvable
from .context import ScheduleSolveContext
from scheduler_api.domain.schedule import Schedule
from scheduler_api.domain.schedule_population import (
    SchedulePopulation,
    ScheduleCandidate,
)
from .pipeline import ScheduleSolvePipeline


class ScheduleSolver(
    Solvable[
        ScheduleSolveContext,
        Schedule,
        SchedulePopulation,
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

    def __init__(self, pipeline_type: str = "default"):
        """
        Args:
            pipeline_type: Type of pipeline to use ('default', 'advanced', 'performance')
        """
        self.pipeline_type = pipeline_type

    def create_context(
        self, template_id: UUID, parameters: dict
    ) -> ScheduleSolveContext:
        """
        Create solve context from template ID and parameters.

        This is a simplified version for testing that doesn't require database access.
        In production, this would fetch template data from the database.

        Args:
            template_id: Template ID (ignored in testing context)
            parameters: Solve parameters

        Returns:
            ScheduleSolveContext with mock data for testing
        """
        from uuid import uuid4

        # Generate mock data for testing
        shift_ids = [uuid4() for _ in range(5)]
        worker_ids = [uuid4() for _ in range(3)]
        skill_a = uuid4()
        skill_b = uuid4()

        # Merge parameters with defaults
        merged_params = {**self.DEFAULT_PARAMETERS, **parameters}

        from .context import ScheduleSolveContext

        return ScheduleSolveContext(
            template_id=template_id,
            shift_ids=shift_ids,
            worker_ids=worker_ids,
            skill_requirements={
                shift_ids[0]: [skill_a],
                shift_ids[1]: [skill_b],
                shift_ids[2]: [skill_a, skill_b],
                shift_ids[3]: [skill_a],
                shift_ids[4]: [skill_b],
            },
            worker_skills={
                worker_ids[0]: [skill_a, skill_b],  # Has both skills
                worker_ids[1]: [skill_a],  # Has skill_a only
                worker_ids[2]: [skill_b],  # Has skill_b only
            },
            parameters=merged_params,
        )

    def create_initial_population(
        self, context: ScheduleSolveContext, size: int
    ) -> SchedulePopulation:
        """Generate initial population of schedules using configured seeder."""
        # Get the pipeline to access the seeder
        pipeline = self.create_pipeline()

        if not pipeline.seeders:
            raise ValueError("No seeder configured in pipeline")

        # Use the first seeder to generate initial population
        seeder = pipeline.seeders[0]
        schedules = seeder.seed(context, size)

        # Convert list of schedules to SchedulePopulation
        population = SchedulePopulation(generation=0)
        for schedule in schedules:
            candidate = ScheduleCandidate(generation=0, genome=schedule, fitness=0.0)
            population.add_candidate(candidate)

        return population

    def create_pipeline(self) -> ScheduleSolvePipeline:
        """Return pipeline configuration with component lists."""
        # Import here to avoid circular imports
        from .composition import SchedulePipelineComposer
        from .seeders.random_seeder import RandomSeeder
        from .mutators.random_assignment_mutator import RandomAssignmentMutator
        from .scorers.skills_match_scorer import SkillsMatchScorer
        from .constraints.no_double_booking_constraint import NoDoubleBookingConstraint
        from .selectors.top_n_selector import TopNSelector
        from scheduler_api.engine.stop_conditions.generation_limit import (
            GenerationLimitStopCondition,
        )

        # Use composition API for enhanced pipelines
        if self.pipeline_type == "advanced":
            return SchedulePipelineComposer.compose_advanced()
        elif self.pipeline_type == "performance":
            return SchedulePipelineComposer.compose_performance()
        elif self.pipeline_type == "custom":
            # Allow custom composition
            return SchedulePipelineComposer.compose_custom(
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
        else:  # "default" or any other
            return SchedulePipelineComposer.compose_default()
