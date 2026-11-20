from __future__ import annotations

from typing import ClassVar
from uuid import UUID

from scheduler_api.engine.models.component_config import (
    CoverageScorerConfig,
)
from scheduler_api.engine.models.component_io import (
    ScoreInput,
    ScoreResult,
    ScoreUpdate,
)
from scheduler_api.engine.models.phase import ComponentCategory


class CoverageScorer:
    """Score staffing coverage per demanded job and slot."""

    component_category: ClassVar[ComponentCategory] = ComponentCategory.SCORER

    def __init__(self, config: CoverageScorerConfig | None = None) -> None:
        self._config = config or CoverageScorerConfig()

    def score(self, input: ScoreInput) -> ScoreResult:
        problem = input.problem
        updates: list[ScoreUpdate] = []

        for individual in input.population.individuals:
            counts: dict[tuple[UUID, int], int] = {}
            for assignment in individual.assignments:
                key = (assignment.job_id, assignment.slot_index)
                counts[key] = counts.get(key, 0) + 1

            accumulated = 0.0
            weight_total = 0.0
            for requirement in problem.staffing_requirements:
                required = requirement.required_workers
                covered = counts.get((requirement.job_id, requirement.slot_index), 0)
                unit = max(required, 1)
                under = max(0, required - covered)
                over = max(0, covered - required)
                quality = (
                    1.0 - under / unit - self._config.overstaffing_weight * over / unit
                )
                quality = max(0.0, min(1.0, quality))
                accumulated += quality * unit
                weight_total += unit

            score = accumulated / weight_total if weight_total else 1.0
            updates.append(ScoreUpdate(individual_id=individual.id, score=score))

        return ScoreResult(category="scorer", updates=tuple(updates))
