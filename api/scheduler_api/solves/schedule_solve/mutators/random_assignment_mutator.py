"""Random assignment mutator for schedule transformation."""

import random
from dataclasses import dataclass
from uuid import UUID
from scheduler_api.engine.interfaces import GenomeOperator
from scheduler_api.domain.schedule import (
    Schedule,
    ShiftAssignment,
    ShiftAssignmentStatus,
)
from ..context import ScheduleSolveContext


@dataclass
class RandomAssignmentMutator(GenomeOperator[Schedule, ScheduleSolveContext]):
    """Mutator that randomly changes worker-shift assignments."""

    name: str = "random_assignment_mutator"

    def apply(self, schedule: Schedule, context: ScheduleSolveContext) -> Schedule:
        """Apply random mutation to schedule."""
        # Create a copy to mutate
        mutated_schedule = schedule.copy()

        # Randomly choose a mutation type
        mutation_type = random.choice(["add", "remove", "swap", "replace"])

        if mutation_type == "add" and context.shift_ids:
            # Add a worker to a random unassigned shift
            assigned_shift_ids = {
                assignment.shift_id for assignment in mutated_schedule.shift_assignments
            }
            unassigned_shifts = [
                shift_id
                for shift_id in context.shift_ids
                if shift_id not in assigned_shift_ids
            ]

            if unassigned_shifts:
                shift_id = random.choice(unassigned_shifts)
                available_workers = context.worker_ids
                if available_workers:
                    worker_id = random.choice(available_workers)
                    assignment = ShiftAssignment(
                        worker_id=worker_id,
                        shift_id=shift_id,
                        status=ShiftAssignmentStatus.ASSIGNED,
                    )
                    mutated_schedule.shift_assignments.append(assignment)

        elif mutation_type == "remove":
            # Remove a random assignment
            if mutated_schedule.shift_assignments:
                assignment_to_remove = random.choice(mutated_schedule.shift_assignments)
                mutated_schedule.shift_assignments.remove(assignment_to_remove)

        elif mutation_type == "swap" and len(context.worker_ids) >= 2:
            # Swap workers between two assignments
            if len(mutated_schedule.shift_assignments) >= 2:
                assignment1, assignment2 = random.sample(
                    mutated_schedule.shift_assignments, 2
                )
                # Swap worker assignments
                assignment1.worker_id, assignment2.worker_id = (
                    assignment2.worker_id,
                    assignment1.worker_id,
                )

        elif mutation_type == "replace" and context.shift_ids and context.worker_ids:
            # Replace a worker assignment
            if mutated_schedule.shift_assignments:
                assignment_to_replace = random.choice(
                    mutated_schedule.shift_assignments
                )
                available_workers = [
                    w
                    for w in context.worker_ids
                    if w != assignment_to_replace.worker_id
                ]
                if available_workers:
                    new_worker_id = random.choice(available_workers)
                    assignment_to_replace.worker_id = new_worker_id

        return mutated_schedule
