from typing import Protocol

from scheduler_api.engine.models.component_io import CullInput, CullResult
from scheduler_api.engine.protocols.component import Component


class Culler(Component, Protocol):
    def cull(self, input: CullInput) -> CullResult: ...
