"""Top-N culler."""

from __future__ import annotations

from scheduler_api.engine.errors import ComponentInputError
from scheduler_api.engine.models.component_io import CullResult, TopNCullInput
from scheduler_api.engine.models.genome import Population
from scheduler_api.engine.ordering import rank_individuals


class TopNCuller:
    """Retains the ``target_size`` best candidates by the canonical ordering.

    With rank-based retention elitism is inherent: the best candidates are kept
    by construction. ``preserve_best`` is validated and recorded so the policy is
    explicit rather than an accident of the operator, and so a future culler with
    different semantics still honours it.
    """

    component_id = "cull_top_n"

    def cull(self, input: TopNCullInput) -> CullResult:
        if input.target_size > len(input.candidates):
            raise ComponentInputError(
                f"cannot retain {input.target_size} candidates from a set of "
                f"{len(input.candidates)}"
            )
        if input.preserve_best > input.target_size:
            raise ComponentInputError("preserve_best must not exceed target_size")
        ranked = rank_individuals(input.candidates)
        retained = ranked[: input.target_size]
        return CullResult(population=Population(individuals=retained))
