"""No double booking constraint for schedule validation."""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from scheduler_api.engine.interfaces import Constraint
from scheduler_api.domain.schedule import Schedule
from ..context import ScheduleSolveContext


@dataclass
class NoDoubleBookingConstraint(Constraint[Schedule, ScheduleSolveContext]):
    """Constraint that prevents workers from being assigned to overlapping shifts."""

    name: str = "no_double_booking_constraint"

    def validate(self, schedule: Schedule, context: ScheduleSolveContext) -> bool:
        """Return True if no worker has overlapping shifts."""
        # Build schedule for each worker
        worker_schedules: dict[UUID, list[tuple[datetime, datetime]]] = {}

        for assignment in schedule.shift_assignments:
            shift_times = context.get_shift_times(assignment.shift_id)
            if not shift_times:
                # Skip shifts without time information
                continue

            start_time, end_time = shift_times
            if assignment.worker_id not in worker_schedules:
                worker_schedules[assignment.worker_id] = []
            worker_schedules[assignment.worker_id].append((start_time, end_time))

        # Check for overlaps for each worker
        for worker_id, shifts in worker_schedules.items():
            # Sort by start time
            sorted_shifts = sorted(shifts, key=lambda x: x[0])

            # Check consecutive shifts for overlap
            for i in range(len(sorted_shifts) - 1):
                current_end = sorted_shifts[i][1]
                next_start = sorted_shifts[i + 1][0]

                if current_end > next_start:
                    return False  # Overlap found

        return True

    def penalty(self, schedule: Schedule, context: ScheduleSolveContext) -> float:
        """Calculate penalty for double booking violations."""
        if not context.shift_schedule:
            # No time information, can't check overlaps
            return 0.0

        worker_schedules: dict[UUID, list[tuple[datetime, datetime]]] = {}
        overlap_count = 0

        # Build schedule for each worker
        for assignment in schedule.shift_assignments:
            shift_times = context.get_shift_times(assignment.shift_id)
            if not shift_times:
                continue

            start_time, end_time = shift_times
            if assignment.worker_id not in worker_schedules:
                worker_schedules[assignment.worker_id] = []
            worker_schedules[assignment.worker_id].append((start_time, end_time))

        # Count overlaps for each worker
        for worker_id, shifts in worker_schedules.items():
            if len(shifts) < 2:
                continue

            # Sort by start time
            sorted_shifts = sorted(shifts, key=lambda x: x[0])

            # Count overlapping pairs
            for i in range(len(sorted_shifts) - 1):
                for j in range(i + 1, len(sorted_shifts)):
                    shift1_end = sorted_shifts[i][1]
                    shift2_start = sorted_shifts[j][0]

                    if shift1_end > shift2_start:
                        overlap_count += 1

        # Penalty increases with number of overlaps
        # Max penalty of 1.0 for severe violations
        max_possible_overlaps = len(context.worker_ids) * (len(context.shift_ids) - 1)
        if max_possible_overlaps > 0:
            return min(1.0, overlap_count / max_possible_overlaps)
        return 0.0
