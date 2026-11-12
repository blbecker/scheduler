"""Synchronous executor."""

from __future__ import annotations

from uuid import UUID

from scheduler_api.engine.execution.runner import ComponentRunner
from scheduler_api.engine.models.phase import PhaseResult
from scheduler_api.engine.protocols.controller import SolverController


class LocalExecutor:
    """Runs a whole execution synchronously through the controller and runner.

    ``execute`` returns nothing by contract; the result is read from the
    execution store, which is the same read path a distributed executor will use.
    """

    def __init__(self, controller: SolverController, runner: ComponentRunner) -> None:
        self._controller = controller
        self._runner = runner

    def execute(self, execution_id: UUID) -> None:
        try:
            plan = self._controller.start(execution_id)
            while plan is not None:
                results = tuple(
                    self._runner.run(invocation) for invocation in plan.invocations
                )
                phase_result = PhaseResult(
                    execution_id=plan.execution_id,
                    phase_execution_id=plan.phase_execution_id,
                    results=results,
                )
                plan = self._controller.complete_phase(plan, phase_result)
        except Exception as exc:
            self._controller.fail(execution_id, f"{type(exc).__name__}: {exc}")
            raise
