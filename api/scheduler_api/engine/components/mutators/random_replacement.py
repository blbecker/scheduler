from __future__ import annotations

import random
from typing import ClassVar
from uuid import UUID

from scheduler_api.engine.exceptions import InvalidComponentInputError
from scheduler_api.engine.models.assignment import Assignment, Individual
from scheduler_api.engine.models.component_config import (
    RandomReplacementMutatorConfig,
)
from scheduler_api.engine.models.component_io import MutateInput, MutateResult
from scheduler_api.engine.models.phase import ComponentCategory
from scheduler_api.engine.models.population import Population
from scheduler_api.engine.randomness import uuid_from_rng


class RandomReplacementMutator:
    """Create offspring by replacing some assignment workers at random."""

    component_category: ClassVar[ComponentCategory] = ComponentCategory.MUTATOR

    def __init__(
        self,
        config: RandomReplacementMutatorConfig | None = None,
    ) -> None:
        self._config = config or RandomReplacementMutatorConfig()

    def mutate(self, input: MutateInput) -> MutateResult:
        parents = input.parents.individuals
        if not parents and input.offspring_count > 0:
            raise InvalidComponentInputError("cannot mutate an empty parent population")

        rng = random.Random(input.rng_seed)
        problem = input.problem
        offspring: list[Individual] = []

        for index in range(input.offspring_count):
            parent = parents[index % len(parents)]
            assignments = list(parent.assignments)

            for _ in range(self._config.replacements_per_offspring):
                if not assignments:
                    break
                assignment_index = rng.randrange(len(assignments))
                current = assignments[assignment_index]
                occupied: set[tuple[int, UUID]] = {
                    (assignment.slot_index, assignment.worker_id)
                    for assignment in assignments
                }
                eligible = [
                    worker
                    for worker in problem.workers
                    if worker.worker_id != current.worker_id
                    and current.slot_index in worker.available_slot_indices
                    and current.job_id in worker.qualified_job_ids
                    and (current.slot_index, worker.worker_id) not in occupied
                ]
                if eligible:
                    replacement = rng.choice(eligible)
                    assignments[assignment_index] = Assignment(
                        worker_id=replacement.worker_id,
                        job_id=current.job_id,
                        slot_index=current.slot_index,
                    )

            offspring.append(
                Individual(
                    id=uuid_from_rng(rng),
                    assignments=tuple(assignments),
                    scores={},
                    violations=(),
                )
            )

        return MutateResult(
            category="mutator",
            offspring=Population(individuals=tuple(offspring)),
        )
