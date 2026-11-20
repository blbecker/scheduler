from typing import Protocol

from scheduler_api.engine.models.component_io import MutateInput, MutateResult
from scheduler_api.engine.protocols.component import Component


class Mutator(Component, Protocol):
    def mutate(self, input: MutateInput) -> MutateResult: ...
