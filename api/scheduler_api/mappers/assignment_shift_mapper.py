from __future__ import annotations

from uuid import UUID

from scheduler_api.engine.models.assignment import Individual
from scheduler_api.engine.models.problem import SchedulingProblem
from scheduler_api.schemas.schedule import CoalescedShift


def coalesce_assignments(
    problem: SchedulingProblem,
    individual: Individual,
) -> tuple[CoalescedShift, ...]:
    """Coalesce contiguous assignments into deterministic shift intervals."""

    groups: dict[tuple[UUID, UUID], list[int]] = {}
    seen: set[tuple[UUID, UUID, int]] = set()

    for assignment in individual.assignments:
        if not 0 <= assignment.slot_index < problem.slot_count:
            raise ValueError(
                f"assignment references slot {assignment.slot_index}, "
                f"valid range is 0..{problem.slot_count - 1}"
            )
        key = (
            assignment.worker_id,
            assignment.job_id,
            assignment.slot_index,
        )
        if key in seen:
            continue
        seen.add(key)
        groups.setdefault((assignment.worker_id, assignment.job_id), []).append(
            assignment.slot_index
        )

    shifts: list[CoalescedShift] = []
    for (worker_id, job_id), slot_indices in groups.items():
        ordered = sorted(slot_indices)
        run = [ordered[0]]
        for slot_index in ordered[1:]:
            if slot_index == run[-1] + 1:
                run.append(slot_index)
                continue
            shifts.append(_build_shift(problem, worker_id, job_id, run))
            run = [slot_index]
        shifts.append(_build_shift(problem, worker_id, job_id, run))

    shifts.sort(
        key=lambda shift: (
            shift.start,
            shift.worker_id.hex,
            shift.job_id.hex,
        )
    )
    return tuple(shifts)


def _build_shift(
    problem: SchedulingProblem,
    worker_id: UUID,
    job_id: UUID,
    slot_indices: list[int],
) -> CoalescedShift:
    first = problem.slots[slot_indices[0]]
    last = problem.slots[slot_indices[-1]]
    return CoalescedShift(
        worker_id=worker_id,
        job_id=job_id,
        start=first.start,
        end=last.end,
        slot_indices=tuple(slot_indices),
    )


__all__ = ["coalesce_assignments"]
