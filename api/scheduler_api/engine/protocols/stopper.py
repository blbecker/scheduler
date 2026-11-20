from typing import Protocol

from scheduler_api.engine.models.component_io import StopInput, StopResult
from scheduler_api.engine.protocols.component import Component


class Stopper(Component, Protocol):
    def should_stop(self, input: StopInput) -> StopResult: ...
