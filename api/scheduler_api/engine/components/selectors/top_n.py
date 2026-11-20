from __future__ import annotations

from typing import ClassVar

from scheduler_api.engine.models.component_io import SelectInput, SelectResult
from scheduler_api.engine.models.phase import ComponentCategory
from scheduler_api.engine.models.population import Population
from scheduler_api.engine.ranking import rank_individuals


class TopNSelector:
    """Select the highest-ranked individuals using feasibility-first order."""

    component_category: ClassVar[ComponentCategory] = ComponentCategory.SELECTOR

    def select(self, input: SelectInput) -> SelectResult:
        ranked = rank_individuals(input.population.individuals, input.scoring_policy)
        selected = ranked[: input.count]
        return SelectResult(
            category="selector",
            selected=Population(individuals=selected),
        )
