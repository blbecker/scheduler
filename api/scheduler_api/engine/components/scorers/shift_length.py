from __future__ import annotations

from typing import ClassVar
from uuid import UUID

from scheduler_api.engine.models.component_config import (
    ShiftLengthScorerConfig,
)
from scheduler_api.engine.models.component_io import (
    ScoreInput,
    ScoreResult,
    ScoreUpdate,
)
from scheduler_api.engine.models.phase import ComponentCategory


class ShiftLengthScorer:
    """Score contiguous worker/job runs against shift-length preferences."""

    component_category: ClassVar[ComponentCategory] = ComponentCategory.SCORER

    def __init__(
        self,
        config: ShiftLengthScorerConfig | None = None,
    ) -> None:
        self._config = config or ShiftLengthScorerConfig()

    def score(self, input: ScoreInput) -> ScoreResult:
        problem = input.problem
        workers = {worker.worker_id: worker for worker in problem.workers}
        updates: list[ScoreUpdate] = []

        for individual in input.population.individuals:
            groups: dict[tuple[UUID, UUID], list[int]] = {}
            for assignment in individual.assignments:
                key = (assignment.worker_id, assignment.job_id)
                groups.setdefault(key, []).append(assignment.slot_index)

            quality_total = 0.0
            run_count = 0
            for (worker_id, _), slot_indices in groups.items():
                indices = sorted(slot_indices)
                runs: list[int] = []
                current = 1
                for previous, current_index in zip(indices, indices[1:]):
                    if current_index == previous + 1:
                        current += 1
                    else:
                        runs.append(current)
                        current = 1
                runs.append(current)

                worker = workers.get(worker_id)
                minimum = worker.minimum_shift_slots if worker else None
                maximum = worker.maximum_shift_slots if worker else None
                for length in runs:
                    quality = 1.0
                    if minimum is not None and length < minimum:
                        quality -= (
                            self._config.under_minimum_weight
                            * (minimum - length)
                            / minimum
                        )
                    if maximum is not None and length > maximum:
                        quality -= (
                            self._config.over_maximum_weight
                            * (length - maximum)
                            / maximum
                        )
                    quality_total += max(0.0, min(1.0, quality))
                    run_count += 1

            score = quality_total / run_count if run_count else 1.0
            updates.append(ScoreUpdate(individual_id=individual.id, score=score))

        return ScoreResult(category="scorer", updates=tuple(updates))
