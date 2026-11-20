from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from scheduler_api.engine.exceptions import (
    ComponentExecutionError,
    ExecutionFailedError,
    UnknownExecutionError,
)
from scheduler_api.engine.execution.local import LocalExecutor
from scheduler_api.engine.execution.runner import TypedComponentRunner
from scheduler_api.engine.models.execution import ExecutionStatus
from scheduler_api.engine.models.phase import (
    ComponentInvocation,
    ComponentResult,
    PhaseType,
)
from scheduler_api.engine.solver import build_mvp_solver

from .factories import make_problem


class RecordingRunner:
    def __init__(self, inner: TypedComponentRunner) -> None:
        self.inner = inner
        self.invocations: list[ComponentInvocation] = []

    def run(self, invocation: ComponentInvocation) -> ComponentResult:
        self.invocations.append(invocation)
        return self.inner.run(invocation)


class FailingRunner:
    def __init__(self, error: Exception) -> None:
        self.error = error

    def run(self, invocation: ComponentInvocation) -> ComponentResult:
        raise self.error


class MalformedRunner:
    def __init__(self, inner: TypedComponentRunner) -> None:
        self.inner = inner

    def run(self, invocation: ComponentInvocation) -> ComponentResult:
        result = self.inner.run(invocation)
        return result.model_copy(update={"invocation_id": uuid4()})


class UnknownController:
    def start(self, execution_id: UUID):
        raise UnknownExecutionError(execution_id)

    def complete_phase(self, plan, result):
        raise AssertionError("not called")

    def fail(self, execution_id, failure):
        raise AssertionError("not called")

    def get_state(self, execution_id):
        raise AssertionError("not called")

    def get_result(self, execution_id):
        raise AssertionError("not called")


def make_solver(**kwargs):
    params = {
        "population_size": 4,
        "random_seed": 5,
        "max_generations": 2,
    }
    params.update(kwargs)
    return build_mvp_solver(**params)


def test_local_executor_completes_mvp_solve():
    solver = make_solver()
    controller = solver.create_controller(make_problem())
    runner = TypedComponentRunner(solver.build_registry())
    executor = LocalExecutor(controller, runner)
    execution_id = UUID(int=1)

    assert executor.execute(execution_id) is None

    result = controller.get_result(execution_id)
    assert result.status is ExecutionStatus.COMPLETED
    assert result.best_individual is not None
    assert result.generation == 2


def test_local_executor_runs_invocations_in_plan_order():
    solver = make_solver(max_generations=1)
    controller = solver.create_controller(make_problem())
    runner = RecordingRunner(TypedComponentRunner(solver.build_registry()))
    executor = LocalExecutor(controller, runner)

    executor.execute(UUID(int=2))

    assert [invocation.component_id for invocation in runner.invocations] == [
        "random_schedule",
        "skills_match",
        "worker_overlap",
        "coverage",
        "shift_length",
        "top_n",
        "random_replacement",
        "skills_match",
        "worker_overlap",
        "coverage",
        "shift_length",
        "top_n",
        "generation_count",
    ]


def test_component_error_marks_execution_failed_with_context():
    solver = make_solver()
    controller = solver.create_controller(make_problem())
    execution_id = UUID(int=3)
    error = ComponentExecutionError(
        "boom",
        component_id="random_schedule",
        invocation_id=uuid4(),
        phase=PhaseType.SEED,
    )
    executor = LocalExecutor(controller, FailingRunner(error))

    with pytest.raises(ExecutionFailedError) as raised:
        executor.execute(execution_id)

    assert raised.value.execution_id == execution_id
    assert raised.value.failure.error_type == "ComponentExecutionError"
    assert raised.value.failure.component_id == "random_schedule"
    assert raised.value.failure.invocation_id == error.invocation_id
    assert raised.value.failure.phase is PhaseType.SEED
    result = controller.get_result(execution_id)
    assert result.status is ExecutionStatus.FAILED
    assert result.failure == raised.value.failure


def test_controller_validation_error_marks_execution_failed():
    solver = make_solver()
    controller = solver.create_controller(make_problem())
    execution_id = UUID(int=4)
    runner = MalformedRunner(TypedComponentRunner(solver.build_registry()))
    executor = LocalExecutor(controller, runner)

    with pytest.raises(ExecutionFailedError) as raised:
        executor.execute(execution_id)

    assert raised.value.failure.error_type == "InvalidPhaseResultError"
    assert raised.value.failure.phase is PhaseType.SEED
    assert controller.get_result(execution_id).status is ExecutionStatus.FAILED


def test_unknown_execution_propagates_without_crashing():
    executor = LocalExecutor(UnknownController(), FailingRunner(RuntimeError()))

    with pytest.raises(UnknownExecutionError):
        executor.execute(UUID(int=5))
