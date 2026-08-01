"""Random seeder for initial population generation."""

import random
from dataclasses import dataclass
from uuid import UUID
from scheduler_api.engine.interfaces import Seeder
from scheduler_api.domain.schedule import (
    Schedule,
    ShiftAssignment,
    ShiftAssignmentStatus,
)
from ..context import ScheduleSolveContext


@dataclass
class RandomSeeder(Seeder[Schedule, ScheduleSolveContext]):
    """Seeder that generates random worker-shift assignments."""

    name: str = "random_seeder"

    def seed(self, context: ScheduleSolveContext, count: int) -> list[Schedule]:
        """Generate random schedules for initial population."""
        schedules = []

        for _ in range(count):
            # Create a new schedule
            schedule = Schedule(name=f"Random Schedule {_}")

            # For each shift, randomly assign workers
            for shift_id in context.shift_ids:
                # Randomly decide if this shift gets an assignment
                if random.random() < 0.7:  # 70% chance of assignment
                    # Randomly select 1 worker for this shift (one-to-one assignment)
                    if context.worker_ids:
                        worker_id = random.choice(context.worker_ids)
                        assignment = ShiftAssignment(
                            worker_id=worker_id,
                            shift_id=shift_id,
                            status=ShiftAssignmentStatus.ASSIGNED,
                        )
                        schedule.shift_assignments.append(assignment)

            schedules.append(schedule)

        return schedules
