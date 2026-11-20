from __future__ import annotations

from typing import ClassVar
from uuid import UUID

from scheduler_api.engine.models.component_io import (
    ScoreInput,
    ScoreResult,
    ScoreUpdate,
)
from scheduler_api.engine.models.phase import ComponentCategory
from scheduler_api.engine.models.scores import Violation, ViolationCode


class WorkerOverlapScorer:
    """Detect multiple assignments for the same worker in one slot."""

    component_category: ClassVar[ComponentCategory] = ComponentCategory.SCORER

    def score(self, input: ScoreInput) -> ScoreResult:
        updates: list[ScoreUpdate] = []

        for individual in input.population.individuals:
            seen: set[tuple[int, UUID]] = set()
            violations: list[Violation] = []
            conflicts = 0

            for assignment in individual.assignments:
                key = (assignment.slot_index, assignment.worker_id)
                if key in seen:
                    conflicts += 1
                    violations.append(
                        Violation(
                            code=ViolationCode.WORKER_DOUBLE_BOOKED,
                            message=(
                                f"worker {assignment.worker_id} is assigned "
                                f"more than once in slot "
                                f"{assignment.slot_index}"
                            ),
                            worker_id=assignment.worker_id,
                            job_id=assignment.job_id,
                            slot_index=assignment.slot_index,
                        )
                    )
                else:
                    seen.add(key)

            total = len(individual.assignments)
            score = 1.0 if not total else 1.0 - conflicts / total
            score = max(0.0, min(1.0, score))
            updates.append(
                ScoreUpdate(
                    individual_id=individual.id,
                    score=score,
                    violations=tuple(violations),
                )
            )

        return ScoreResult(category="scorer", updates=tuple(updates))
