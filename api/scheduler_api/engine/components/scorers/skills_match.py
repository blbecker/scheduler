"""Skills match scorer: qualification of the workers actually scheduled."""

from __future__ import annotations

from uuid import UUID

from scheduler_api.engine.components.scorers._common import percentage, resolve_worker
from scheduler_api.engine.models.component_io import (
    SkillsMatchScoreInput,
    SkillsMatchScoreResult,
)
from scheduler_api.engine.models.scores import Violation, ViolationCode


class SkillsMatchScorer:
    """Share of scheduled minutes worked by qualified workers.

    Also reports an unqualified assignment as a hard violation, which is what
    actually makes the candidate infeasible.
    """

    component_id = "skills_match"

    def score(self, input: SkillsMatchScoreInput) -> SkillsMatchScoreResult:
        scores: dict[UUID, float] = {}
        violations: dict[UUID, tuple[Violation, ...]] = {}
        for individual in input.individuals:
            total = qualified = 0
            found: list[Violation] = []
            for shift in individual.shifts:
                total += shift.minutes
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
                if shift.job_id in worker.qualified_job_ids:
                    qualified += shift.minutes
                else:
                    found.append(
                        Violation(
                            code=ViolationCode.WORKER_UNQUALIFIED,
                            worker_id=shift.worker_id,
                            job_id=shift.job_id,
                            shift_id=shift.shift_id,
                            start=shift.start,
                            end=shift.end,
                            detail="worker is not qualified for this job",
                        )
                    )
            scores[individual.id] = percentage(qualified, total)
            violations[individual.id] = tuple(found)
        return SkillsMatchScoreResult(scores=scores, violations=violations)
