from enum import Enum


class ScheduleSolveStatus(str, Enum):
    pending = "pending"
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class ShiftAssignmentStatus(str, Enum):
    ASSIGNED = "assigned"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
