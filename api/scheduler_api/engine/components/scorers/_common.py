"""Helpers shared by scorers."""

from __future__ import annotations

from scheduler_api.engine.models.genome import PlannedShift
from scheduler_api.engine.models.problem import SchedulingProblem, WorkerInfo
from scheduler_api.engine.models.scores import SCORE_MAX, SCORE_MIN


def percentage(part: float, whole: float, *, default: float = 100.0) -> float:
    """``part / whole`` as a 0-100 score, clamped and guarded against zero."""
    if whole <= 0:
        return default
    return max(SCORE_MIN, min(SCORE_MAX, 100.0 * part / whole))


def resolve_worker(
    problem: SchedulingProblem, shift: PlannedShift
) -> WorkerInfo | None:
    """The worker named by a shift, or ``None`` when the reference is unknown."""
    return problem.worker(shift.worker_id)
