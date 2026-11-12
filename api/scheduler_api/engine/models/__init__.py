"""Engine DTOs."""

from scheduler_api.engine.models.execution import (
    ExecutionRequest,
    ExecutionState,
    ExecutionStatus,
    SolverSettings,
)
from scheduler_api.engine.models.fitness import FitnessConfig, compute_fitness
from scheduler_api.engine.models.genome import Individual, PlannedShift, Population
from scheduler_api.engine.models.problem import (
    CoverageRequirement,
    JobInfo,
    ScheduleLimits,
    SchedulingProblem,
    ShiftLengthPolicy,
    TimeWindow,
    WorkerInfo,
    validate_problem_context,
)
from scheduler_api.engine.models.results import CandidateSchedule, ExecutionResult
from scheduler_api.engine.models.scores import Violation, ViolationCode

__all__ = [
    "CandidateSchedule",
    "CoverageRequirement",
    "ExecutionRequest",
    "ExecutionResult",
    "ExecutionState",
    "ExecutionStatus",
    "FitnessConfig",
    "Individual",
    "JobInfo",
    "PlannedShift",
    "Population",
    "ScheduleLimits",
    "SchedulingProblem",
    "ShiftLengthPolicy",
    "SolverSettings",
    "TimeWindow",
    "Violation",
    "ViolationCode",
    "WorkerInfo",
    "compute_fitness",
    "validate_problem_context",
]
