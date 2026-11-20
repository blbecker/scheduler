from __future__ import annotations

from typing import ClassVar

from scheduler_api.engine.models.component_config import (
    GenerationCountStopperConfig,
)
from scheduler_api.engine.models.component_io import StopInput, StopResult
from scheduler_api.engine.models.phase import ComponentCategory


class GenerationCountStopper:
    """Stop once the configured number of reproduction cycles is reached."""

    component_category: ClassVar[ComponentCategory] = ComponentCategory.STOPPER

    def __init__(
        self,
        config: GenerationCountStopperConfig | None = None,
    ) -> None:
        self._config = config or GenerationCountStopperConfig()

    def should_stop(self, input: StopInput) -> StopResult:
        should_stop = input.generation >= self._config.max_generations
        reason = (
            f"generation_limit:{self._config.max_generations}" if should_stop else None
        )
        return StopResult(
            category="stopper",
            should_stop=should_stop,
            reason=reason,
        )
