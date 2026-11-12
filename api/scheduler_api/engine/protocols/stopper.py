"""Stopper contract."""

from __future__ import annotations

from typing import Protocol, TypeVar

from scheduler_api.engine.models.component_io import (
    GenerationCountStopInput,
    StopResult,
)

StopInputT = TypeVar("StopInputT", bound=GenerationCountStopInput, contravariant=True)
StopResultT = TypeVar("StopResultT", bound=StopResult, covariant=True)


class Stopper(Protocol[StopInputT, StopResultT]):
    """Decides whether the execution should terminate."""

    component_id: str

    def should_stop(self, input: StopInputT, /) -> StopResultT: ...
