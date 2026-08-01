from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Any
from uuid import UUID, uuid4
from copy import deepcopy


class ShiftAssignmentStatus(Enum):
    ASSIGNED = "assigned"


@dataclass
class ShiftAssignment:
    shift_id: UUID
    worker_id: Optional[UUID] = None
    status: ShiftAssignmentStatus = ShiftAssignmentStatus.ASSIGNED

    def copy(self) -> "ShiftAssignment":
        """Create a copy of this assignment (immutable pattern)."""
        return ShiftAssignment(
            worker_id=self.worker_id, shift_id=self.shift_id, status=self.status
        )


@dataclass
class Schedule:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    shift_assignments: list[ShiftAssignment] = field(default_factory=list)
    fitness: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def copy(self) -> "Schedule":
        """Create a copy of this schedule (immutable pattern for genetic algorithm)."""
        return Schedule(
            id=self.id,
            name=self.name,
            shift_assignments=[
                assignment.copy() for assignment in self.shift_assignments
            ],
            fitness=self.fitness,
            created_at=self.created_at,
        )

    def get_assigned_workers(self) -> list[UUID]:
        """Get all unique worker IDs assigned across all shifts."""
        worker_ids = [
            assignment.worker_id
            for assignment in self.shift_assignments
            if assignment.worker_id is not None
        ]
        return list(set(worker_ids))

    def get_shifts_for_worker(self, worker_id: UUID) -> list[UUID]:
        """Get all shift IDs where a worker is assigned."""
        return [
            assignment.shift_id
            for assignment in self.shift_assignments
            if assignment.worker_id == worker_id
        ]

    def get_assignment_for_shift(self, shift_id: UUID) -> Optional[ShiftAssignment]:
        """Get the assignment for a specific shift, if any."""
        for assignment in self.shift_assignments:
            if assignment.shift_id == shift_id:
                return assignment
        return None

    def has_assignment_for_shift(self, shift_id: UUID) -> bool:
        """Check if a shift has an assignment."""
        return self.get_assignment_for_shift(shift_id) is not None

    def calculate_fitness(self) -> float:
        """Calculate or return cached fitness score."""
        if self.fitness is not None:
            return self.fitness
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert schedule to dictionary representation."""
        return {
            "id": str(self.id),
            "name": self.name,
            "shift_assignments": [
                {
                    "worker_id": (
                        str(assignment.worker_id) if assignment.worker_id else None
                    ),
                    "shift_id": str(assignment.shift_id),
                    "status": assignment.status.value,
                }
                for assignment in self.shift_assignments
            ],
            "fitness": self.fitness,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Schedule":
        """Create schedule from dictionary representation."""
        schedule = cls(
            id=UUID(data["id"]) if "id" in data else uuid4(),
            name=data.get("name", ""),
            fitness=data.get("fitness"),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else datetime.utcnow()
            ),
        )

        if "shift_assignments" in data:
            for assignment_data in data["shift_assignments"]:
                assignment = ShiftAssignment(
                    worker_id=(
                        UUID(assignment_data["worker_id"])
                        if assignment_data.get("worker_id")
                        else None
                    ),
                    shift_id=UUID(assignment_data["shift_id"]),
                    status=ShiftAssignmentStatus(
                        assignment_data.get("status", "assigned")
                    ),
                )
                schedule.shift_assignments.append(assignment)

        return schedule
