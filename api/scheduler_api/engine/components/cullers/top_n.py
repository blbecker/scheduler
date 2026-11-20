from __future__ import annotations

from typing import ClassVar

from scheduler_api.engine.exceptions import PopulationSizeMismatchError
from scheduler_api.engine.models.component_io import CullInput, CullResult
from scheduler_api.engine.models.phase import ComponentCategory
from scheduler_api.engine.models.population import Population
from scheduler_api.engine.ranking import rank_individuals


class TopNCuller:
    """Keep the best candidates while preserving mandatory elites."""

    component_category: ClassVar[ComponentCategory] = ComponentCategory.CULLER

    def cull(self, input: CullInput) -> CullResult:
        candidates = input.population.individuals
        if len(candidates) < input.target_size:
            raise PopulationSizeMismatchError(input.target_size, len(candidates))

        elite_ids = {individual.id for individual in input.elite_individuals}
        if len(elite_ids) > input.target_size:
            raise PopulationSizeMismatchError(input.target_size, len(elite_ids))

        ranked = rank_individuals(candidates, input.scoring_policy)
        selected = list(ranked[: input.target_size])
        selected_ids = {individual.id for individual in selected}

        for elite in input.elite_individuals:
            if elite.id in selected_ids:
                continue
            replacement_index = next(
                (
                    index
                    for index in range(len(selected) - 1, -1, -1)
                    if selected[index].id not in elite_ids
                ),
                None,
            )
            if replacement_index is None:
                raise PopulationSizeMismatchError(input.target_size, len(selected))
            removed = selected[replacement_index]
            selected_ids.discard(removed.id)
            selected[replacement_index] = elite
            selected_ids.add(elite.id)

        selected = list(rank_individuals(tuple(selected), input.scoring_policy))
        return CullResult(
            category="culler",
            population=Population(individuals=tuple(selected)),
        )
