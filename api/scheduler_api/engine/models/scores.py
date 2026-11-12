"""Scores and violations.

Scores and violations are separate channels and are never mixed: scores are
fitness, violations are feasibility. A candidate is feasible if and only if it
carries no violations.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

#: A component score is always on this closed interval.
SCORE_MIN = 0.0
SCORE_MAX = 100.0


class ViolationCode(StrEnum):
    """Stable identifiers for rule breaches.

    Treat these as an API: the application layer aggregates on them.
    """

    WORKER_UNAVAILABLE = "worker_unavailable"
    WORKER_UNQUALIFIED = "worker_unqualified"
    WORKER_DOUBLE_BOOKED = "worker_double_booked"
    SHIFT_TOO_SHORT = "shift_too_short"
    SHIFT_TOO_LONG = "shift_too_long"
    SHIFT_OUTSIDE_DEMAND = "shift_outside_demand"
    WEEKLY_HOURS_EXCEEDED = "weekly_hours_exceeded"
    SHIFTS_PER_DAY_EXCEEDED = "shifts_per_day_exceeded"
    UNKNOWN_REFERENCE = "unknown_reference"


class Violation(BaseModel):
    """One breach of a rule, with enough context to be legible and aggregable."""

    model_config = ConfigDict(frozen=True)

    code: ViolationCode
    job_id: UUID | None = None
    worker_id: UUID | None = None
    start: datetime | None = None
    end: datetime | None = None
    shift_id: UUID | None = None
    detail: str = ""

    def aggregation_key(self) -> tuple[str, str, str]:
        """Key used when the application layer aggregates violations for display."""
        return (self.code.value, str(self.worker_id or ""), str(self.job_id or ""))
