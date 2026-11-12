"""Generation count stopper."""

from __future__ import annotations

from scheduler_api.engine.models.component_io import (
    GenerationCountStopInput,
    StopResult,
)


class GenerationCountStopper:
    """Stops once the configured number of generations has been evaluated.

    ``maximum_generations`` counts the seeded generation, so a value of 1 evaluates
    the seed population and stops.
    """

    component_id = "generation_count"

    def should_stop(self, input: GenerationCountStopInput) -> StopResult:
        limit = input.config.maximum_generations
        stop = input.generation + 1 >= limit
        reason = (
            f"reached generation limit of {limit}"
            if stop
            else f"generation {input.generation + 1} of {limit} complete"
        )
        return StopResult(should_stop=stop, reason=reason)
