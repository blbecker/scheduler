"""Swap assignment mutator for schedule transformation."""

import random
from dataclasses import dataclass
from uuid import UUID
from scheduler_api.engine.interfaces import GenomeOperator
from scheduler_api.domain.schedule import Schedule
from ..context import ScheduleSolveContext


@dataclass
class SwapAssignmentMutator(GenomeOperator[Schedule, ScheduleSolveContext]):
    """Mutator that swaps workers between shifts."""

    name: str = "swap_assignment_mutator"

    def apply(self, schedule: Schedule, context: ScheduleSolveContext) -> Schedule:
        """Swap workers between two random assignments."""
        # Create a copy to mutate
        mutated_schedule = schedule.copy()

        # Need at least 2 assignments to perform a swap
        if len(mutated_schedule.shift_assignments) < 2:
            return mutated_schedule

        # Select two distinct assignments
        assignment1, assignment2 = random.sample(mutated_schedule.shift_assignments, 2)

        # Swap workers
        assignment1.worker_id, assignment2.worker_id = (
            assignment2.worker_id,
            assignment1.worker_id,
        )

        return mutated_schedule
