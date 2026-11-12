"""Overstaffing scorer: assigned minutes beyond what demand requires."""

from __future__ import annotations

from uuid import UUID

from scheduler_api.engine.components.scorers._common import percentage
from scheduler_api.engine.intervals import measure_coverage
from scheduler_api.engine.models.component_io import (
    OverstaffingScoreInput,
    OverstaffingScoreResult,
)


class OverstaffingScorer:
    """Penalizes labor minutes that no demand window asked for.

    100 means no excess minutes anywhere; lower means wasted staffing.
    """

    component_id = "overstaffing"

    def score(self, input: OverstaffingScoreInput) -> OverstaffingScoreResult:
        problem = input.problem
        job_ids = tuple(job.job_id for job in problem.jobs)
        scores: dict[UUID, float] = {}
        for individual in input.individuals:
            required = excess = 0
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
                required += measurement.required_minutes
                excess += measurement.excess_minutes
            scores[individual.id] = percentage(max(0, required - excess), required)
        return OverstaffingScoreResult(scores=scores)
