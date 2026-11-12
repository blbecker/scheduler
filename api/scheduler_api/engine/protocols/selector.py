"""Selector contract."""

from __future__ import annotations

from typing import Protocol, TypeVar

from scheduler_api.engine.models.component_io import SelectResult, TopNSelectInput

SelectInputT = TypeVar("SelectInputT", bound=TopNSelectInput, contravariant=True)
SelectResultT = TypeVar("SelectResultT", bound=SelectResult, covariant=True)


class Selector(Protocol[SelectInputT, SelectResultT]):
    """Chooses individuals for reproduction."""

    component_id: str

    def select(self, input: SelectInputT, /) -> SelectResultT: ...
