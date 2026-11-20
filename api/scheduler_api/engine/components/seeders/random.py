from __future__ import annotations

import random
from typing import ClassVar
from uuid import UUID

from scheduler_api.engine.models.assignment import Assignment, Individual
from scheduler_api.engine.models.component_config import (
    RandomScheduleSeederConfig,
)
from scheduler_api.engine.models.component_io import SeedInput, SeedResult
from scheduler_api.engine.models.phase import ComponentCategory
from scheduler_api.engine.models.population import Population
from scheduler_api.engine.randomness import uuid_from_rng


class RandomScheduleSeeder:
    component_category: ClassVar[ComponentCategory] = ComponentCategory.SEEDER

    def __init__(
        self,
        config: RandomScheduleSeederConfig | None = None,
    ) -> None:
        self._config = config or RandomScheduleSeederConfig()

    def seed(self, input: SeedInput) -> SeedResult:
        rng = random.Random(input.rng_seed)
        problem = input.problem
        individuals: list[Individual] = []

        for _ in range(input.population_size):
            demand_rows = list(problem.staffing_requirements)
            if self._config.shuffle_demand_order:
                rng.shuffle(demand_rows)

            assigned_slots: set[tuple[int, UUID]] = set()
            assignments: list[Assignment] = []
            for row in demand_rows:
                if row.required_workers == 0:
                    continue
                candidates = [
                    worker
                    for worker in problem.workers
                    if row.slot_index in worker.available_slot_indices
                    and row.job_id in worker.qualified_job_ids
                    and (row.slot_index, worker.worker_id) not in assigned_slots
                ]
                rng.shuffle(candidates)
                for worker in candidates[: row.required_workers]:
                    assignments.append(
                        Assignment(
                            worker_id=worker.worker_id,
                            job_id=row.job_id,
                            slot_index=row.slot_index,
                        )
                    )
                    assigned_slots.add((row.slot_index, worker.worker_id))

            individuals.append(
                Individual(
                    id=uuid_from_rng(rng),
                    assignments=tuple(assignments),
                )
            )

        return SeedResult(
            category="seeder",
            population=Population(individuals=tuple(individuals)),
        )
