"""Double-booking scorer: overlapping shifts for the same worker."""

from __future__ import annotations

from uuid import UUID

from scheduler_api.engine.components.scorers._common import percentage, resolve_worker
from scheduler_api.engine.intervals import overlap_minutes
from scheduler_api.engine.models.component_io import (
    DoubleBookingScoreInput,
    DoubleBookingScoreResult,
)
from scheduler_api.engine.models.genome import PlannedShift
from scheduler_api.engine.models.scores import Violation, ViolationCode


class DoubleBookingScorer:
    """Finds shifts that overlap for one worker and reports each overlap."""

    component_id = "double_booking"

    def score(self, input: DoubleBookingScoreInput) -> DoubleBookingScoreResult:
        scores: dict[UUID, float] = {}
        violations: dict[UUID, tuple[Violation, ...]] = {}
        for individual in input.individuals:
            by_worker: dict[UUID, list[PlannedShift]] = {}
            found: list[Violation] = []
            total = 0
            for shift in individual.shifts:
                total += shift.minutes
                if resolve_worker(input.problem, shift) is None:
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
                by_worker.setdefault(shift.worker_id, []).append(shift)
            conflicting = 0
            for worker_id, shifts in by_worker.items():
                ordered = sorted(shifts, key=lambda shift: shift.start)
                for index, shift in enumerate(ordered):
                    for other in ordered[index + 1 :]:
                        if other.start >= shift.end:
                            break
                        minutes = overlap_minutes(
                            shift.start, shift.end, other.start, other.end
                        )
                        if minutes <= 0:
                            continue
                        conflicting += minutes
                        found.append(
                            Violation(
                                code=ViolationCode.WORKER_DOUBLE_BOOKED,
                                worker_id=worker_id,
                                job_id=shift.job_id,
                                shift_id=shift.shift_id,
                                start=shift.start,
                                end=shift.end,
                                detail=f"overlaps another shift by {minutes} minutes",
                            )
                        )
            scores[individual.id] = percentage(max(0, total - conflicting), total)
            violations[individual.id] = tuple(found)
        return DoubleBookingScoreResult(scores=scores, violations=violations)
