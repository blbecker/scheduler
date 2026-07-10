"""Skills match scorer for evaluating schedule genomes."""

from dataclasses import dataclass
from uuid import UUID
from ...interfaces import Scorable
from ..genome import ScheduleGenome
from ..context import ScheduleSolveContext


@dataclass
class SkillsMatchScorer(Scorable[ScheduleGenome, ScheduleSolveContext]):
    """Scorer that evaluates skill matches between workers and shifts."""

    name: str = "skills_match_scorer"

    def score(self, genome: ScheduleGenome, context: ScheduleSolveContext) -> float:
        """Calculate skill match score for genome."""
        if not genome.assignments:
            return 0.0

        total_score = 0.0
        total_shifts = len(context.shift_ids)

        for shift_id, assigned_workers in genome.assignments.items():
            shift_score = self._score_shift(shift_id, assigned_workers, context)
            total_score += shift_score

        # Normalize score to [0, 1] range
        if total_shifts > 0:
            return total_score / total_shifts
        return 0.0

    def _score_shift(
        self,
        shift_id: UUID,
        assigned_workers: list[UUID],
        context: ScheduleSolveContext,
    ) -> float:
        """Calculate score for a single shift."""
        required_skills = set(context.get_shift_skills(shift_id))

        if not required_skills:
            # No skills required, perfect score if at least one worker assigned
            return 1.0 if assigned_workers else 0.0

        if not assigned_workers:
            # Shift has requirements but no workers assigned
            return 0.0

        # Get union of all skills from assigned workers
        available_skills: set[UUID] = set()
        for worker_id in assigned_workers:
            worker_skills = context.get_worker_skills(worker_id)
            available_skills.update(worker_skills)

        # Calculate coverage: how many required skills are covered
        covered_skills = required_skills.intersection(available_skills)
        coverage_ratio = len(covered_skills) / len(required_skills)

        # Penalize overstaffing (too many workers for the shift)
        staffing_penalty = 0.0
        if len(assigned_workers) > 2:  # More than 2 workers is excessive
            staffing_penalty = 0.1 * (len(assigned_workers) - 2)

        return max(0.0, coverage_ratio - staffing_penalty)
