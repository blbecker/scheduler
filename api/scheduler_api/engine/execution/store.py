"""Execution storage.

The MVP keeps everything in memory, but results are still read through this
interface so a distributed executor can share one read path later.
"""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from scheduler_api.engine.errors import ExecutionNotFoundError
from scheduler_api.engine.models.execution import ExecutionRequest, ExecutionState
from scheduler_api.engine.models.results import ExecutionResult


class ExecutionStore(Protocol):
    def save_request(self, request: ExecutionRequest) -> None: ...

    def load_request(self, execution_id: UUID) -> ExecutionRequest: ...

    def save_state(self, state: ExecutionState) -> None: ...

    def load_state(self, execution_id: UUID) -> ExecutionState: ...

    def save_result(self, result: ExecutionResult) -> None: ...

    def load_result(self, execution_id: UUID) -> ExecutionResult | None: ...


class InMemoryExecutionStore:
    """Process-local store. Not thread-safe; one execution per id."""

    def __init__(self) -> None:
        self._requests: dict[UUID, ExecutionRequest] = {}
        self._states: dict[UUID, ExecutionState] = {}
        self._results: dict[UUID, ExecutionResult] = {}

    def save_request(self, request: ExecutionRequest) -> None:
        self._requests[request.execution_id] = request

    def load_request(self, execution_id: UUID) -> ExecutionRequest:
        request = self._requests.get(execution_id)
        if request is None:
            raise ExecutionNotFoundError(f"no execution request for {execution_id}")
        return request

    def save_state(self, state: ExecutionState) -> None:
        self._states[state.execution_id] = state

    def load_state(self, execution_id: UUID) -> ExecutionState:
        state = self._states.get(execution_id)
        if state is None:
            raise ExecutionNotFoundError(f"no execution state for {execution_id}")
        return state

    def save_result(self, result: ExecutionResult) -> None:
        self._results[result.execution_id] = result

    def load_result(self, execution_id: UUID) -> ExecutionResult | None:
        return self._results.get(execution_id)
