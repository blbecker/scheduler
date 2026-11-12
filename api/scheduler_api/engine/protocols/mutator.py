"""Mutator contract."""

from __future__ import annotations

from typing import Protocol, TypeVar

from scheduler_api.engine.models.component_io import (
    MutateResult,
    RandomShiftMutateInput,
)

MutateInputT = TypeVar("MutateInputT", bound=RandomShiftMutateInput, contravariant=True)
MutateResultT = TypeVar("MutateResultT", bound=MutateResult, covariant=True)


class Mutator(Protocol[MutateInputT, MutateResultT]):
    """Creates changed candidates from selected parents.

    Recombination, when added, is a strategy inside a mutator, not a new protocol.
    """

    component_id: str

    def mutate(self, input: MutateInputT, /) -> MutateResultT: ...
