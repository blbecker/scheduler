from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from scheduler_api.engine.models.solver_spec import SolverSpec

if TYPE_CHECKING:
    from scheduler_api.engine.execution.registry import ComponentRegistry


class Solver(Protocol):
    def build_registry(self) -> ComponentRegistry: ...

    def to_spec(self) -> SolverSpec: ...
