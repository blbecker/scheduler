"""Availability scorer: assigned minutes that fall outside a worker's windows."""

from __future__ import annotations

from uuid import UUID

from scheduler_api.engine.components.scorers._common import percentage, resolve_worker
from scheduler_api.engine.intervals import minutes_inside
from scheduler_api.engine.models.component_io import (
    AvailabilityScoreInput,
    AvailabilityScoreResult,
)
from scheduler_api.engine.models.scores import Violation, ViolationCode


class AvailabilityScorer:
    """Reports unavailable assignments as violations and scores inside-window minutes."""

    component_id = "availability"

    def score(self, input: AvailabilityScoreInput) -> AvailabilityScoreResult:
        scores: dict[UUID, float] = {}
        violations: dict[UUID, tuple[Violation, ...]] = {}
        for individual in input.individuals:
            total = inside = 0
            found: list[Violation] = []
            for shift in individual.shifts:
                duration = shift.minutes
                total += duration
                worker = resolve_worker(input.problem, shift)
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
                    continue
                available = [window.interval for window in worker.available_windows]
                covered = minutes_inside(shift.start, shift.end, available)
                inside += covered
                if covered < duration:
                    found.append(
                        Violation(
                            code=ViolationCode.WORKER_UNAVAILABLE,
                            worker_id=shift.worker_id,
                            job_id=shift.job_id,
                            shift_id=shift.shift_id,
                            start=shift.start,
                            end=shift.end,
                            detail=f"{duration - covered} minutes fall outside availability",
                        )
                    )
            scores[individual.id] = percentage(inside, total)
            violations[individual.id] = tuple(found)
        return AvailabilityScoreResult(scores=scores, violations=violations)
