"""Coverage scorer: how much required demand is actually staffed."""

from __future__ import annotations

from uuid import UUID

from scheduler_api.engine.components.scorers._common import percentage
from scheduler_api.engine.intervals import measure_coverage, minutes_inside
from scheduler_api.engine.models.component_io import (
    CoverageScoreInput,
    CoverageScoreResult,
)
from scheduler_api.engine.models.scores import Violation, ViolationCode


class CoverageScorer:
    """Measures covered requirement-minutes against total requirement-minutes.

    100 means demand is met at every instant; 0 means nothing is covered. Shifts
    that serve no demand at all are reported as violations rather than scored.
    """

    component_id = "coverage"

    def score(self, input: CoverageScoreInput) -> CoverageScoreResult:
        problem = input.problem
        job_ids = tuple(job.job_id for job in problem.jobs)
        scores: dict[UUID, float] = {}
        violations: dict[UUID, tuple[Violation, ...]] = {}
        for individual in input.individuals:
            covered = required = 0
            for job_id in job_ids:
                demand = [
                    (requirement.start, requirement.end, requirement.required_workers)
                    for requirement in problem.requirements
                    if requirement.job_id == job_id
                ]
                assigned = [
                    (shift.start, shift.end)
                    for shift in individual.shifts
                    if shift.job_id == job_id
                ]
                measurement = measure_coverage(demand, assigned)
                covered += measurement.covered_minutes
                required += measurement.required_minutes
            found: list[Violation] = []
            for shift in individual.shifts:
                windows = [
                    (requirement.start, requirement.end)
                    for requirement in problem.requirements
                    if requirement.job_id == shift.job_id
                ]
                if shift.job_id not in job_ids:
                    found.append(
                        Violation(
                            code=ViolationCode.UNKNOWN_REFERENCE,
                            job_id=shift.job_id,
                            worker_id=shift.worker_id,
                            shift_id=shift.shift_id,
                            start=shift.start,
                            end=shift.end,
                            detail="shift names a job that is not in the problem",
                        )
                    )
                elif minutes_inside(shift.start, shift.end, windows) == 0:
                    found.append(
                        Violation(
                            code=ViolationCode.SHIFT_OUTSIDE_DEMAND,
                            job_id=shift.job_id,
                            worker_id=shift.worker_id,
                            shift_id=shift.shift_id,
                            start=shift.start,
                            end=shift.end,
                            detail="shift overlaps no demand window for its job",
                        )
                    )
            scores[individual.id] = percentage(covered, required)
            violations[individual.id] = tuple(found)
        return CoverageScoreResult(scores=scores, violations=violations)
