from typing import Protocol

from scheduler_api.engine.models.component_io import SeedInput, SeedResult
from scheduler_api.engine.protocols.component import Component


class Seeder(Component, Protocol):
    def seed(self, input: SeedInput) -> SeedResult: ...
