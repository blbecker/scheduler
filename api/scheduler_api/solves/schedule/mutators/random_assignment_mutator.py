"""Random assignment mutator for genome transformation."""

import random
from dataclasses import dataclass
from typing import List
from uuid import UUID
from ...interfaces import GenomeOperator
from ..genome import ScheduleGenome
from ..context import ScheduleSolveContext


@dataclass
class RandomAssignmentMutator(GenomeOperator[ScheduleGenome, ScheduleSolveContext]):
    """Mutator that randomly changes worker-shift assignments."""

    name: str = "random_assignment_mutator"

    def apply(
        self, genome: ScheduleGenome, context: ScheduleSolveContext
    ) -> ScheduleGenome:
        """Apply random mutation to genome."""
        # Create a copy to mutate
        mutated_genome = genome.copy()

        # Randomly choose a mutation type
        mutation_type = random.choice(["add", "remove", "swap", "replace"])

        if mutation_type == "add" and context.shift_ids:
            # Add a worker to a random shift
            shift_id = random.choice(context.shift_ids)
            available_workers = [
                w
                for w in context.worker_ids
                if w not in mutated_genome.assignments.get(shift_id, [])
            ]
            if available_workers:
                worker_id = random.choice(available_workers)
                mutated_genome.assignments.setdefault(shift_id, []).append(worker_id)

        elif mutation_type == "remove":
            # Remove a worker from a random shift
            shifts_with_workers = [
                s for s, w in mutated_genome.assignments.items() if w
            ]
            if shifts_with_workers:
                shift_id = random.choice(shifts_with_workers)
                if mutated_genome.assignments[shift_id]:
                    worker_id = random.choice(mutated_genome.assignments[shift_id])
                    mutated_genome.assignments[shift_id].remove(worker_id)

        elif mutation_type == "swap" and len(context.worker_ids) >= 2:
            # Swap workers between two shifts
            shifts_with_workers = [
                s for s, w in mutated_genome.assignments.items() if len(w) >= 1
            ]
            if len(shifts_with_workers) >= 2:
                shift1, shift2 = random.sample(shifts_with_workers, 2)
                if (
                    mutated_genome.assignments[shift1]
                    and mutated_genome.assignments[shift2]
                ):
                    worker1 = random.choice(mutated_genome.assignments[shift1])
                    worker2 = random.choice(mutated_genome.assignments[shift2])
                    mutated_genome.assignments[shift1].remove(worker1)
                    mutated_genome.assignments[shift1].append(worker2)
                    mutated_genome.assignments[shift2].remove(worker2)
                    mutated_genome.assignments[shift2].append(worker1)

        elif mutation_type == "replace" and context.shift_ids and context.worker_ids:
            # Replace a worker assignment
            shifts_with_workers = [
                s for s, w in mutated_genome.assignments.items() if w
            ]
            if shifts_with_workers:
                shift_id = random.choice(shifts_with_workers)
                old_worker = random.choice(mutated_genome.assignments[shift_id])
                available_workers = [
                    w
                    for w in context.worker_ids
                    if w != old_worker
                    and w not in mutated_genome.assignments.get(shift_id, [])
                ]
                if available_workers:
                    new_worker = random.choice(available_workers)
                    mutated_genome.assignments[shift_id].remove(old_worker)
                    mutated_genome.assignments[shift_id].append(new_worker)

        return mutated_genome
