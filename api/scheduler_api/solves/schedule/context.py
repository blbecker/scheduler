"""Schedule solve context with repository access."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from uuid import UUID
from datetime import datetime


@dataclass
class ScheduleSolveContext:
    """Context for schedule solve execution with repository access."""

    template_id: UUID
    """ID of the schedule template being solved"""

    worker_ids: List[UUID] = field(default_factory=list)
    """List of available worker IDs"""

    shift_ids: List[UUID] = field(default_factory=list)
    """List of shift IDs that need assignments"""

    skill_requirements: Dict[UUID, List[UUID]] = field(default_factory=dict)
    """Mapping of shift_id -> list of required skill IDs"""

    worker_skills: Dict[UUID, List[UUID]] = field(default_factory=dict)
    """Mapping of worker_id -> list of skill IDs they have"""

    shift_schedule: Dict[UUID, Tuple[datetime, datetime]] = field(default_factory=dict)
    """Mapping of shift_id -> (start_time, end_time)"""

    parameters: Dict = field(default_factory=dict)
    """Solve parameters (population_size, max_generations, etc.)"""

    def get_shift_skills(self, shift_id: UUID) -> List[UUID]:
        """Get required skills for a shift."""
        return self.skill_requirements.get(shift_id, [])

    def get_worker_skills(self, worker_id: UUID) -> List[UUID]:
        """Get skills possessed by a worker."""
        return self.worker_skills.get(worker_id, [])

    def get_shift_times(self, shift_id: UUID) -> Optional[Tuple[datetime, datetime]]:
        """Get start and end times for a shift."""
        return self.shift_schedule.get(shift_id)

    def has_worker(self, worker_id: UUID) -> bool:
        """Check if worker is available in this context."""
        return worker_id in self.worker_ids

    def has_shift(self, shift_id: UUID) -> bool:
        """Check if shift exists in this context."""
        return shift_id in self.shift_ids
