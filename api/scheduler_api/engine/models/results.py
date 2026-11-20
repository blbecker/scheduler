from __future__ import annotations

from uuid import UUID

from .assignment import Individual
from .base import EngineModel
from .execution import ExecutionStatus, FailureInfo


class ExecutionResult(EngineModel):
    execution_id: UUID
    status: ExecutionStatus
    generation: int
    best_individual: Individual | None
    best_total_score: float | None
    best_feasible: bool
    termination_reason: str | None
    failure: FailureInfo | None
