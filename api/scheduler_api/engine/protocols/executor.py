"""Executor contract."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID


class SolverExecutor(Protocol):
    """Determines how planned component invocations are run."""

    def execute(self, execution_id: UUID) -> None: ...
