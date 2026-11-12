"""Culler contract."""

from __future__ import annotations

from typing import Protocol, TypeVar

from scheduler_api.engine.models.component_io import CullResult, TopNCullInput

CullInputT = TypeVar("CullInputT", bound=TopNCullInput, contravariant=True)
CullResultT = TypeVar("CullResultT", bound=CullResult, covariant=True)


class Culler(Protocol[CullInputT, CullResultT]):
    """Reduces a candidate set to the population size for the next generation."""

    component_id: str

    def cull(self, input: CullInputT, /) -> CullResultT: ...
