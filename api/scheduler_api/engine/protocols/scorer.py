"""Scorer contract."""

from __future__ import annotations

from typing import Protocol, TypeVar

from scheduler_api.engine.models.component_io import ScoreInput, ScoreResult

ScoreInputT = TypeVar("ScoreInputT", bound=ScoreInput, contravariant=True)
ScoreResultT = TypeVar("ScoreResultT", bound=ScoreResult, covariant=True)


class Scorer(Protocol[ScoreInputT, ScoreResultT]):
    """Evaluates candidates against one criterion.

    Returns scores on a 0-100 scale plus any structured violations.
    """

    component_id: str

    def score(self, input: ScoreInputT, /) -> ScoreResultT: ...
