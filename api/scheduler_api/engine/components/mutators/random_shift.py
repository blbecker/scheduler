"""Random shift mutator.

A weighted mix of reassigning a shift's worker, nudging a boundary, deleting a
shift, and inserting a shift for uncovered demand. Every boundary move is snapped
to the boundary grid and clamped to the effective hard shift-length bounds:
unbounded mutation fragments coverage into shifts that are infeasible rather than
merely unfit.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from uuid import UUID

from scheduler_api.engine.determinism import derive_uuid
from scheduler_api.engine.errors import ComponentResultError
from scheduler_api.engine.intervals import minutes_inside, overlaps
from scheduler_api.engine.models.component_io import (
    MutateResult,
    RandomShiftMutateInput,
)
from scheduler_api.engine.models.genome import Individual, PlannedShift
from scheduler_api.engine.models.problem import SchedulingProblem, WorkerInfo
from scheduler_api.engine.models.time import minutes_between
from scheduler_api.engine.policies import effective_bounds


class RandomShiftMutator:
    """Produces offspring by random shift-level edits of selected parents."""

    component_id = "random_shift"

    def mutate(self, input: RandomShiftMutateInput) -> MutateResult:
        if not input.parents:
            raise ComponentResultError("mutation requires at least one parent")
        rng = random.Random(input.random_seed)
        offspring: list[Individual] = []
        for index in range(input.offspring_count):
            parent = input.parents[index % len(input.parents)]
            shifts = list(parent.shifts)
            for _ in range(input.config.mutations_per_offspring):
                shifts = self._mutate_once(input, shifts, rng, index)
            offspring.append(
                Individual(
                    id=derive_uuid(input.random_seed, "offspring", index),
                    shifts=tuple(shifts),
                )
            )
        ids = [individual.id for individual in offspring]
        if len(set(ids)) != len(ids):
            raise ComponentResultError("mutator produced duplicate individual ids")
        return MutateResult(individuals=tuple(offspring))

    def _mutate_once(
        self,
        input: RandomShiftMutateInput,
        shifts: list[PlannedShift],
        rng: random.Random,
        offspring_index: int,
    ) -> list[PlannedShift]:
        config = input.config
        strategies: list[tuple[float, str]] = [
            (config.weight_reassign_worker, "reassign"),
            (config.weight_nudge_boundary, "nudge"),
            (config.weight_delete_shift, "delete"),
            (config.weight_insert_shift, "insert"),
        ]
        total_weight = sum(weight for weight, _ in strategies)
        if total_weight <= 0:
            return shifts
        pick = rng.random() * total_weight
        chosen = strategies[-1][1]
        for weight, name in strategies:
            if pick < weight:
                chosen = name
                break
            pick -= weight
        if chosen == "reassign":
            return self._reassign_worker(input.problem, shifts, rng)
        if chosen == "nudge":
            return self._nudge_boundary(input.problem, shifts, rng)
        if chosen == "delete":
            return self._delete_shift(shifts, rng)
        return self._insert_shift(
            input.problem,
            shifts,
            rng,
            derive_uuid(input.random_seed, "insert", offspring_index),
        )

    def _reassign_worker(
        self, problem: SchedulingProblem, shifts: list[PlannedShift], rng: random.Random
    ) -> list[PlannedShift]:
        if not shifts:
            return shifts
        index = rng.randrange(len(shifts))
        target = shifts[index]
        candidates = [
            worker
            for worker in problem.workers
            if target.job_id in worker.qualified_job_ids
            and worker.worker_id != target.worker_id
        ]
        rng.shuffle(candidates)
        for worker in candidates:
            available = [window.interval for window in worker.available_windows]
            if minutes_inside(target.start, target.end, available) != target.minutes:
                continue
            if self._has_conflict(
                shifts, index, worker.worker_id, target.start, target.end
            ):
                continue
            replacement = target.model_copy(update={"worker_id": worker.worker_id})
            return [*shifts[:index], replacement, *shifts[index + 1 :]]
        return shifts

    def _nudge_boundary(
        self, problem: SchedulingProblem, shifts: list[PlannedShift], rng: random.Random
    ) -> list[PlannedShift]:
        if not shifts:
            return shifts
        index = rng.randrange(len(shifts))
        target = shifts[index]
        worker = problem.worker(target.worker_id)
        if worker is None:
            return shifts
        minimum, maximum = effective_bounds(worker, problem.shifts)
        grid = problem.boundary_granularity_minutes
        delta = timedelta(minutes=grid * rng.choice((-2, -1, 1, 2)))
        move_start = rng.random() < 0.5
        start = target.start + delta if move_start else target.start
        end = target.end if move_start else target.end + delta
        if end <= start:
            return shifts
        if start < problem.horizon_start or end > problem.horizon_end:
            return shifts
        duration = minutes_between(start, end)
        if duration < minimum or duration > maximum:
            return shifts
        available = [window.interval for window in worker.available_windows]
        if minutes_inside(start, end, available) != duration:
            return shifts
        if self._has_conflict(shifts, index, worker.worker_id, start, end):
            return shifts
        moved = target.model_copy(
            update={"start": start, "end": end, "shift_id": target.shift_id}
        )
        return [*shifts[:index], moved, *shifts[index + 1 :]]

    def _delete_shift(
        self, shifts: list[PlannedShift], rng: random.Random
    ) -> list[PlannedShift]:
        if len(shifts) <= 1:
            return shifts
        index = rng.randrange(len(shifts))
        return [*shifts[:index], *shifts[index + 1 :]]

    def _insert_shift(
        self,
        problem: SchedulingProblem,
        shifts: list[PlannedShift],
        rng: random.Random,
        shift_id: UUID,
    ) -> list[PlannedShift]:
        requirement = rng.choice(problem.requirements)
        qualified = [
            worker
            for worker in problem.workers
            if requirement.job_id in worker.qualified_job_ids
        ]
        if not qualified:
            return shifts
        grid = problem.boundary_granularity_minutes
        window_minutes = minutes_between(requirement.start, requirement.end)
        if window_minutes < grid:
            return shifts
        for _ in range(6):
            worker = rng.choice(qualified)
            start, end = self._sample_interval(
                problem,
                worker,
                requirement.start,
                requirement.end,
                window_minutes,
                grid,
                rng,
            )
            if start is None or end is None:
                continue
            available = [window.interval for window in worker.available_windows]
            duration = minutes_between(start, end)
            if minutes_inside(start, end, available) != duration:
                continue
            if any(
                shift.worker_id == worker.worker_id
                and overlaps(start, end, shift.start, shift.end)
                for shift in shifts
            ):
                continue
            inserted = PlannedShift(
                shift_id=shift_id,
                worker_id=worker.worker_id,
                job_id=requirement.job_id,
                start=start,
                end=end,
            )
            return [*shifts, inserted]
        return shifts

    @staticmethod
    def _sample_interval(
        problem: SchedulingProblem,
        worker: WorkerInfo,
        window_start: datetime,
        window_end: datetime,
        window_minutes: int,
        grid: int,
        rng: random.Random,
    ) -> tuple[datetime | None, datetime | None]:
        minimum, maximum = effective_bounds(worker, problem.shifts)
        low = max(grid, -(-minimum // grid) * grid)
        high = min(maximum, (window_minutes // grid) * grid)
        if high < low:
            return (None, None)
        duration = low + rng.randrange((high - low) // grid + 1) * grid
        latest_start = window_minutes - duration
        if latest_start < 0:
            return (None, None)
        offset = rng.randrange(latest_start // grid + 1) * grid
        start = window_start + timedelta(minutes=offset)
        end = start + timedelta(minutes=duration)
        if end > window_end:
            return (None, None)
        return (start, end)

    @staticmethod
    def _has_conflict(
        shifts: list[PlannedShift],
        skip_index: int,
        worker_id: UUID,
        start: datetime,
        end: datetime,
    ) -> bool:
        return any(
            index != skip_index
            and shift.worker_id == worker_id
            and overlaps(start, end, shift.start, shift.end)
            for index, shift in enumerate(shifts)
        )
