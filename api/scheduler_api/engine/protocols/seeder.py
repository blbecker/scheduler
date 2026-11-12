"""Seeder contract."""

from __future__ import annotations

from typing import Protocol, TypeVar

from scheduler_api.engine.models.component_io import SeedRandomShiftsInput, SeedResult

SeedInputT = TypeVar("SeedInputT", bound=SeedRandomShiftsInput, contravariant=True)
SeedResultT = TypeVar("SeedResultT", bound=SeedResult, covariant=True)


class Seeder(Protocol[SeedInputT, SeedResultT]):
    """Creates the initial population."""

    component_id: str

    def seed(self, input: SeedInputT, /) -> SeedResultT: ...
