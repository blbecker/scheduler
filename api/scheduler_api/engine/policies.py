"""Shift-length policy resolution.

Scorers and mutators must resolve bounds through this module. Duplicated bound
logic is how a mutator ends up emitting shifts that a scorer calls infeasible.
"""

from __future__ import annotations

from scheduler_api.engine.models.problem import ShiftLengthPolicy, WorkerInfo


def effective_bounds(worker: WorkerInfo, policy: ShiftLengthPolicy) -> tuple[int, int]:
    """Hard ``(minimum, maximum)`` shift length in minutes for one worker."""
    minimum = (
        worker.minimum_shift_minutes
        if worker.minimum_shift_minutes is not None
        else policy.minimum_minutes
    )
    maximum = (
        worker.maximum_shift_minutes
        if worker.maximum_shift_minutes is not None
        else policy.maximum_minutes
    )
    return minimum, maximum


def effective_preferred_bounds(
    worker: WorkerInfo, policy: ShiftLengthPolicy
) -> tuple[int | None, int | None]:
    """Soft ``(minimum, maximum)`` shift length preference for one worker.

    ``None`` means the worker expressed no preference on that side; a preference
    scorer treats unexpressed sides as always satisfied.
    """
    return (
        worker.preferred_minimum_shift_minutes,
        worker.preferred_maximum_shift_minutes,
    )


def fits_bounds(duration_minutes: int, bounds: tuple[int, int]) -> bool:
    """True when a duration satisfies hard bounds."""
    minimum, maximum = bounds
    return minimum <= duration_minutes <= maximum


def clamp_duration(duration_minutes: int, bounds: tuple[int, int]) -> int:
    """Clamp a duration into hard bounds."""
    minimum, maximum = bounds
    return max(minimum, min(maximum, duration_minutes))
