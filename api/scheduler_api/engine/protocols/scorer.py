from typing import Protocol

from scheduler_api.engine.models.component_io import ScoreInput, ScoreResult
from scheduler_api.engine.protocols.component import Component


class Scorer(Component, Protocol):
    def score(self, input: ScoreInput) -> ScoreResult: ...
