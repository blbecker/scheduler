from uuid import UUID

from typing import Protocol


class SolverExecutor(Protocol):
    def execute(self, execution_id: UUID) -> None: ...
