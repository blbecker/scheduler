from __future__ import annotations

from uuid import UUID

from .models.phase import ComponentCategory, PhaseType
from .models.results import FailureInfo


class EngineError(Exception):
    def __init__(
        self,
        message: str,
        *,
        component_id: str | None = None,
        invocation_id: UUID | None = None,
        phase: PhaseType | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.component_id = component_id
        self.invocation_id = invocation_id
        self.phase = phase


class EngineValidationError(EngineError):
    pass


class SolverConfigurationError(EngineValidationError):
    pass


class InvalidIndividualError(EngineValidationError):
    pass


class DuplicateIndividualError(EngineValidationError):
    pass


class PopulationSizeMismatchError(EngineValidationError):
    def __init__(
        self,
        expected: int,
        actual: int,
        *,
        component_id: str | None = None,
    ) -> None:
        super().__init__(
            f"population size mismatch: expected {expected}, got {actual}",
            component_id=component_id,
        )
        self.expected = expected
        self.actual = actual


class ComponentNotFoundError(EngineError):
    def __init__(
        self,
        component_id: str,
        category: ComponentCategory,
        *,
        phase: PhaseType | None = None,
    ) -> None:
        super().__init__(
            f"component not found: {category.value}:{component_id}",
            component_id=component_id,
            phase=phase,
        )
        self.category = category


class DuplicateComponentError(EngineError):
    def __init__(
        self,
        component_id: str,
        category: ComponentCategory,
    ) -> None:
        super().__init__(
            f"duplicate component: {category.value}:{component_id}",
            component_id=component_id,
        )
        self.category = category


class ComponentCategoryMismatchError(EngineError):
    pass


class InvalidComponentInputError(EngineError):
    pass


class InvalidComponentResultError(EngineError):
    pass


class ComponentExecutionError(EngineError):
    pass


class PhaseError(EngineError):
    pass


class UnknownExecutionError(PhaseError):
    def __init__(self, execution_id: UUID) -> None:
        super().__init__(f"unknown execution: {execution_id}")
        self.execution_id = execution_id


class StalePhaseResultError(PhaseError):
    def __init__(self, phase_execution_id: UUID) -> None:
        super().__init__(f"stale phase result: {phase_execution_id}")
        self.phase_execution_id = phase_execution_id


class InvalidPhaseResultError(PhaseError):
    pass


class DuplicateInvocationError(PhaseError):
    def __init__(self, invocation_id: UUID) -> None:
        super().__init__(f"duplicate invocation: {invocation_id}")
        self.invocation_id = invocation_id


class MissingScorerOutputError(PhaseError):
    def __init__(self, individual_id: UUID, scorer_id: str) -> None:
        super().__init__(
            f"missing output from scorer {scorer_id} "
            f"for individual {individual_id}",
            component_id=scorer_id,
        )
        self.individual_id = individual_id
        self.scorer_id = scorer_id


class DuplicateScoreError(PhaseError):
    def __init__(self, individual_id: UUID, scorer_id: str) -> None:
        super().__init__(
            f"duplicate score from {scorer_id} for individual {individual_id}",
            component_id=scorer_id,
        )
        self.individual_id = individual_id
        self.scorer_id = scorer_id


class ExecutionFailedError(EngineError):
    def __init__(self, execution_id: UUID, failure: FailureInfo) -> None:
        super().__init__(
            f"execution {execution_id} failed: {failure.error_type}: "
            f"{failure.message}",
            phase=failure.phase,
            component_id=failure.component_id,
            invocation_id=failure.invocation_id,
        )
        self.execution_id = execution_id
        self.failure = failure
