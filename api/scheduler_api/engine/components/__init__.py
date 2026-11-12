"""Concrete GA operators.

Components are stateless: configuration arrives in the invocation input DTO.
They never import the controller, the executor, Celery, or persistence.
"""

from scheduler_api.engine.components.cullers.top_n import TopNCuller
from scheduler_api.engine.components.mutators.random_shift import RandomShiftMutator
from scheduler_api.engine.components.scorers.availability import AvailabilityScorer
from scheduler_api.engine.components.scorers.coverage import CoverageScorer
from scheduler_api.engine.components.scorers.double_booking import DoubleBookingScorer
from scheduler_api.engine.components.scorers.overstaffing import OverstaffingScorer
from scheduler_api.engine.components.scorers.schedule_limits import ScheduleLimitsScorer
from scheduler_api.engine.components.scorers.shift_length import ShiftLengthScorer
from scheduler_api.engine.components.scorers.skills_match import SkillsMatchScorer
from scheduler_api.engine.components.seeders.random_shifts import RandomShiftSeeder
from scheduler_api.engine.components.selectors.top_n import TopNSelector
from scheduler_api.engine.components.stoppers.generation_count import (
    GenerationCountStopper,
)

__all__ = [
    "AvailabilityScorer",
    "CoverageScorer",
    "DoubleBookingScorer",
    "GenerationCountStopper",
    "OverstaffingScorer",
    "RandomShiftMutator",
    "RandomShiftSeeder",
    "ScheduleLimitsScorer",
    "ShiftLengthScorer",
    "SkillsMatchScorer",
    "TopNCuller",
    "TopNSelector",
]
