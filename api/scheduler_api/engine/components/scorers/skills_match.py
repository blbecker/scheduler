from __future__ import annotations

from typing import ClassVar

from scheduler_api.engine.models.component_config import (
    SkillsMatchScorerConfig,
)
from scheduler_api.engine.models.component_io import (
    ScoreInput,
    ScoreResult,
    ScoreUpdate,
)
from scheduler_api.engine.models.phase import ComponentCategory
from scheduler_api.engine.models.scores import Violation, ViolationCode


class SkillsMatchScorer:
    """Score assignments against worker qualifications and availability."""

    component_category: ClassVar[ComponentCategory] = ComponentCategory.SCORER

    def __init__(
        self,
        config: SkillsMatchScorerConfig | None = None,
    ) -> None:
        self._config = config or SkillsMatchScorerConfig()

    def score(self, input: ScoreInput) -> ScoreResult:
        problem = input.problem
        workers = {worker.worker_id: worker for worker in problem.workers}
        job_ids = {job.job_id for job in problem.jobs}
        slot_count = problem.slot_count
        updates: list[ScoreUpdate] = []

        for individual in input.population.individuals:
            violations: list[Violation] = []
            eligible = 0

            for assignment in individual.assignments:
                assignment_violations: list[Violation] = []
                worker = workers.get(assignment.worker_id)
                slot_valid = 0 <= assignment.slot_index < slot_count

                if worker is None:
                    assignment_violations.append(
                        Violation(
                            code=ViolationCode.UNKNOWN_WORKER,
                            message=(
                                f"worker {assignment.worker_id} is not in "
                                "the problem"
                            ),
                            worker_id=assignment.worker_id,
                            job_id=assignment.job_id,
                            slot_index=assignment.slot_index,
                        )
                    )
                if assignment.job_id not in job_ids:
                    assignment_violations.append(
                        Violation(
                            code=ViolationCode.UNKNOWN_JOB,
                            message=(
                                f"job {assignment.job_id} is not in " "the problem"
                            ),
                            worker_id=assignment.worker_id,
                            job_id=assignment.job_id,
                            slot_index=assignment.slot_index,
                        )
                    )
                if not slot_valid:
                    assignment_violations.append(
                        Violation(
                            code=ViolationCode.SLOT_OUT_OF_RANGE,
                            message=(
                                f"slot {assignment.slot_index} is outside "
                                f"0..{slot_count - 1}"
                            ),
                            worker_id=assignment.worker_id,
                            job_id=assignment.job_id,
                            slot_index=assignment.slot_index,
                        )
                    )
                if (
                    worker is not None
                    and assignment.job_id in job_ids
                    and assignment.job_id not in worker.qualified_job_ids
                ):
                    assignment_violations.append(
                        Violation(
                            code=ViolationCode.UNQUALIFIED_WORKER,
                            message=(
                                f"worker {assignment.worker_id} is not "
                                f"qualified for job {assignment.job_id}"
                            ),
                            worker_id=assignment.worker_id,
                            job_id=assignment.job_id,
                            slot_index=assignment.slot_index,
                        )
                    )
                if (
                    self._config.check_availability
                    and worker is not None
                    and slot_valid
                    and assignment.slot_index not in worker.available_slot_indices
                ):
                    assignment_violations.append(
                        Violation(
                            code=ViolationCode.UNAVAILABLE_WORKER,
                            message=(
                                f"worker {assignment.worker_id} is not "
                                f"available for slot "
                                f"{assignment.slot_index}"
                            ),
                            worker_id=assignment.worker_id,
                            job_id=assignment.job_id,
                            slot_index=assignment.slot_index,
                        )
                    )

                if not assignment_violations:
                    eligible += 1
                violations.extend(assignment_violations)

            total = len(individual.assignments)
            score = eligible / total if total else 1.0
            updates.append(
                ScoreUpdate(
                    individual_id=individual.id,
                    score=score,
                    violations=tuple(violations),
                )
            )

        return ScoreResult(category="scorer", updates=tuple(updates))
