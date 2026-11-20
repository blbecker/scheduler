from __future__ import annotations

from typing import Protocol
from uuid import UUID

from scheduler_api.engine.models.execution import ExecutionState
from scheduler_api.engine.models.phase import PhasePlan, PhaseResult
from scheduler_api.engine.models.results import ExecutionResult, FailureInfo


class SolverController(Protocol):
    def start(self, execution_id: UUID) -> PhasePlan | None: ...

    def complete_phase(
        self, plan: PhasePlan, result: PhaseResult
    ) -> PhasePlan | None: ...

    def fail(self, execution_id: UUID, failure: FailureInfo) -> None: ...

    def get_state(self, execution_id: UUID) -> ExecutionState: ...

    def get_result(self, execution_id: UUID) -> ExecutionResult: ...


__all__ = ["SolverController"]
