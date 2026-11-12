"""Shift length scorer: hard bounds as violations, preferences as score."""

from __future__ import annotations

from uuid import UUID

from scheduler_api.engine.components.scorers._common import percentage, resolve_worker
from scheduler_api.engine.models.component_io import (
    ShiftLengthScoreInput,
    ShiftLengthScoreResult,
)
from scheduler_api.engine.models.problem import SchedulingProblem, WorkerInfo
from scheduler_api.engine.models.scores import Violation, ViolationCode
from scheduler_api.engine.policies import effective_bounds, effective_preferred_bounds


def preference_deficit(
    problem: SchedulingProblem, worker: WorkerInfo, duration: int
) -> int:
    """Minutes by which a duration misses the worker's expressed preferences."""
    preferred_minimum, preferred_maximum = effective_preferred_bounds(
        worker, problem.shifts
    )
    deficit = 0
    if preferred_minimum is not None and duration < preferred_minimum:
        deficit += preferred_minimum - duration
    if preferred_maximum is not None and duration > preferred_maximum:
        deficit += duration - preferred_maximum
    return deficit


class ShiftLengthScorer:
    """Enforces organization and per-worker hard bounds; scores preferences.

    A shift outside hard bounds is a violation (the candidate is infeasible). A
    shift outside the worker's *preferred* bounds only costs score.
    """

    component_id = "shift_length"

    def score(self, input: ShiftLengthScoreInput) -> ShiftLengthScoreResult:
        problem = input.problem
        scores: dict[UUID, float] = {}
        violations: dict[UUID, tuple[Violation, ...]] = {}
        for individual in input.individuals:
            total = satisfied = 0
            found: list[Violation] = []
            for shift in individual.shifts:
                duration = shift.minutes
                total += duration
                worker = resolve_worker(problem, shift)
                if worker is None:
                    found.append(
                        Violation(
                            code=ViolationCode.UNKNOWN_REFERENCE,
                            worker_id=shift.worker_id,
                            job_id=shift.job_id,
                            shift_id=shift.shift_id,
                            start=shift.start,
                            end=shift.end,
                            detail="shift names a worker that is not in the problem",
                        )
                    )
                    satisfied += duration
                    continue
                minimum, maximum = effective_bounds(worker, problem.shifts)
                if duration < minimum:
                    found.append(
                        Violation(
                            code=ViolationCode.SHIFT_TOO_SHORT,
                            worker_id=shift.worker_id,
                            job_id=shift.job_id,
                            shift_id=shift.shift_id,
                            start=shift.start,
                            end=shift.end,
                            detail=f"{duration} minutes is below the hard minimum of {minimum}",
                        )
                    )
                elif duration > maximum:
                    found.append(
                        Violation(
                            code=ViolationCode.SHIFT_TOO_LONG,
                            worker_id=shift.worker_id,
                            job_id=shift.job_id,
                            shift_id=shift.shift_id,
                            start=shift.start,
                            end=shift.end,
                            detail=f"{duration} minutes exceeds the hard maximum of {maximum}",
                        )
                    )
                satisfied += duration - preference_deficit(problem, worker, duration)
            scores[individual.id] = percentage(satisfied, total)
            violations[individual.id] = tuple(found)
        return ShiftLengthScoreResult(scores=scores, violations=violations)
