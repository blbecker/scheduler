from __future__ import annotations

from uuid import UUID

from scheduler_api.engine.exceptions import (
    EngineError,
    ExecutionFailedError,
    UnknownExecutionError,
)
from scheduler_api.engine.models.execution import FailureInfo
from scheduler_api.engine.models.phase import PhasePlan, PhaseResult
from scheduler_api.engine.protocols.controller import SolverController
from scheduler_api.engine.protocols.runner import Runner


def _failure_info(error: EngineError, plan: PhasePlan | None) -> FailureInfo:
    phase = error.phase
    if phase is None and plan is not None:
        phase = plan.phase
    return FailureInfo(
        error_type=type(error).__name__,
        message=str(error),
        phase=phase,
        component_id=error.component_id,
        invocation_id=error.invocation_id,
    )


class LocalExecutor:
    """Run every phase of one synchronous GA execution in process."""

    def __init__(
        self,
        controller: SolverController,
        runner: Runner,
    ) -> None:
        self._controller = controller
        self._runner = runner

    def execute(self, execution_id: UUID) -> None:
        plan: PhasePlan | None = None
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
        except UnknownExecutionError:
            # There is no execution state to mark failed.
            raise
        except EngineError as error:
            failure = _failure_info(error, plan)
            self._controller.fail(execution_id, failure)
            raise ExecutionFailedError(execution_id, failure) from error
        except Exception as error:  # defensive, not control flow
            failure = FailureInfo(
                error_type=type(error).__name__,
                message=str(error),
                phase=plan.phase if plan is not None else None,
            )
            self._controller.fail(execution_id, failure)
            raise ExecutionFailedError(execution_id, failure) from error


__all__ = ["LocalExecutor"]
