"""Top-N selector."""

from __future__ import annotations

from scheduler_api.engine.errors import ComponentInputError
from scheduler_api.engine.models.component_io import SelectResult, TopNSelectInput
from scheduler_api.engine.ordering import rank_individuals


class TopNSelector:
    """Selects the ``count`` best individuals by the canonical ordering."""

    component_id = "select_top_n"

    def select(self, input: TopNSelectInput) -> SelectResult:
        if input.count > len(input.individuals):
            raise ComponentInputError(
                f"cannot select {input.count} individuals from a population of "
                f"{len(input.individuals)}"
            )
        ranked = rank_individuals(input.individuals)
        return SelectResult(individuals=ranked[: input.count])
