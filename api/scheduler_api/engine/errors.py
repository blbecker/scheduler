"""Engine exception hierarchy.

Engine errors are explicit and carry enough context to identify the execution,
phase, component, and invocation involved.
"""

from __future__ import annotations

from uuid import UUID


class EngineError(Exception):
    """Base class for every error raised by the engine."""


class ProblemValidationError(EngineError):
    """The scheduling problem context is malformed or internally inconsistent."""


class UnknownComponentError(EngineError):
    """A component id was not registered."""


class ComponentCategoryError(EngineError):
    """A component was resolved with the wrong category, or a mismatch was found."""


class ComponentInputError(EngineError):
    """A component invocation input failed validation."""


class ComponentResultError(EngineError):
    """A component produced a result the engine refuses to accept."""


class PhaseResultError(EngineError):
    """A phase result does not match the phase plan it claims to complete."""


class ExecutionNotFoundError(EngineError):
    """No execution request or state exists for the given id."""


class ExecutionStateError(EngineError):
    """The execution is not in a state that permits the requested operation."""


class ComponentExecutionError(EngineError):
    """A component raised while executing an invocation."""

    def __init__(
        self,
        message: str,
        *,
        execution_id: UUID | None = None,
        phase_execution_id: UUID | None = None,
        component_id: str | None = None,
        invocation_id: UUID | None = None,
    ) -> None:
        context = []
        if execution_id is not None:
            context.append(f"execution={execution_id}")
        if phase_execution_id is not None:
            context.append(f"phase_execution={phase_execution_id}")
        if component_id is not None:
            context.append(f"component={component_id}")
        if invocation_id is not None:
            context.append(f"invocation={invocation_id}")
        suffix = f" ({', '.join(context)})" if context else ""
        super().__init__(f"{message}{suffix}")
        self.execution_id = execution_id
        self.phase_execution_id = phase_execution_id
        self.component_id = component_id
        self.invocation_id = invocation_id
