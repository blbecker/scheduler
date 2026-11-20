from typing import Protocol

from scheduler_api.engine.models.component_io import SelectInput, SelectResult
from scheduler_api.engine.protocols.component import Component


class Selector(Component, Protocol):
    def select(self, input: SelectInput) -> SelectResult: ...
