"""Random seeder for initial population generation."""

import random
from dataclasses import dataclass
from typing import List
from uuid import UUID
from ...interfaces import Seeder
from ..genome import ScheduleGenome
from ..context import ScheduleSolveContext


@dataclass
class RandomSeeder(Seeder[ScheduleGenome, ScheduleSolveContext]):
    """Seeder that generates random worker-shift assignments."""

    name: str = "random_seeder"

    def seed(self, context: ScheduleSolveContext, count: int) -> List[ScheduleGenome]:
        """Generate random genomes for initial population."""
        genomes = []

        for _ in range(count):
            assignments = {}

            # Assign workers to shifts randomly
            for shift_id in context.shift_ids:
                # Randomly select 0-2 workers for this shift
                num_workers = random.randint(0, min(2, len(context.worker_ids)))
                if num_workers > 0:
                    assigned_workers = random.sample(context.worker_ids, num_workers)
                    assignments[shift_id] = assigned_workers
                else:
                    # Leave shift unassigned
                    assignments[shift_id] = []

            genome = ScheduleGenome(assignments=assignments)
            genomes.append(genome)

        return genomes
