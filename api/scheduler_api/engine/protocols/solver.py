"""Solver contract.

A solver is an orchestration object: it describes the GA elements that make up an
algorithm. It contains no execution logic.
"""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from scheduler_api.engine.models.execution import ExecutionRequest, SolverSettings
from scheduler_api.engine.models.problem import SchedulingProblem


class Solver(Protocol):
    """Describes an algorithm and can describe an execution of itself."""

    component_id: str

    @property
    def settings(self) -> SolverSettings: ...

    def build_request(
        self,
        *,
        execution_id: UUID,
        problem: SchedulingProblem,
        random_seed: int,
    ) -> ExecutionRequest: ...
