"""Controller contract."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from scheduler_api.engine.models.phase import PhasePlan, PhaseResult
from scheduler_api.engine.models.results import ExecutionResult


class SolverController(Protocol):
    """Owns the execution lifecycle state machine."""

    def start(self, execution_id: UUID) -> PhasePlan | None: ...

    def complete_phase(
        self, plan: PhasePlan, result: PhaseResult
    ) -> PhasePlan | None: ...

    def result(self, execution_id: UUID) -> ExecutionResult: ...

    def fail(self, execution_id: UUID, reason: str) -> None: ...
