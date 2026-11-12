"""Random schedule seeder.

Samples shifts inside demand windows for qualified, available workers, respecting
hard shift-length bounds and the boundary grid. It aims for structurally valid and
mostly feasible output, not for quality: scorers judge what it produces.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from uuid import UUID

from scheduler_api.engine.determinism import derive_uuid
from scheduler_api.engine.intervals import minutes_inside, overlaps
from scheduler_api.engine.models.component_io import SeedRandomShiftsInput, SeedResult
from scheduler_api.engine.models.genome import Individual, PlannedShift, Population
from scheduler_api.engine.models.problem import SchedulingProblem, WorkerInfo
from scheduler_api.engine.models.time import minutes_between, snap_to_grid
from scheduler_api.engine.policies import effective_bounds

#: Attempts to place one coverage unit before giving up on it.
_PLACEMENT_ATTEMPTS = 8


class RandomShiftSeeder:
    """Builds candidate schedules by random placement against demand."""

    component_id = "random_shifts"

    def seed(self, input: SeedRandomShiftsInput) -> SeedResult:
        rng = random.Random(input.random_seed)
        individuals = tuple(
            self._build_individual(input.problem, rng, index, input.random_seed)
            for index in range(input.population_size)
        )
        return SeedResult(population=Population(individuals=individuals))

    def _build_individual(
        self,
        problem: SchedulingProblem,
        rng: random.Random,
        index: int,
        seed: int,
    ) -> Individual:
        individual_id = derive_uuid(seed, "seed", index)
        shifts: list[PlannedShift] = []
        for requirement in problem.requirements:
            qualified = [
                worker
                for worker in problem.workers
                if requirement.job_id in worker.qualified_job_ids
            ]
            if not qualified:
                continue
            for _ in range(requirement.required_workers):
                shift = self._place_shift(
                    problem=problem,
                    rng=rng,
                    existing=shifts,
                    qualified=qualified,
                    job_id=requirement.job_id,
                    window_start=requirement.start,
                    window_end=requirement.end,
                    individual_id=individual_id,
                    ordinal=len(shifts),
                )
                if shift is not None:
                    shifts.append(shift)
        return Individual(id=individual_id, shifts=tuple(shifts))

    def _place_shift(
        self,
        *,
        problem: SchedulingProblem,
        rng: random.Random,
        existing: list[PlannedShift],
        qualified: list[WorkerInfo],
        job_id: UUID,
        window_start: datetime,
        window_end: datetime,
        individual_id: UUID,
        ordinal: int,
    ) -> PlannedShift | None:
        window_minutes = minutes_between(window_start, window_end)
        if window_minutes <= 0:
            return None
        grid = problem.boundary_granularity_minutes
        aligned_start = snap_to_grid(window_start, grid, direction="up")
        lead_in = minutes_between(window_start, aligned_start)
        for _ in range(_PLACEMENT_ATTEMPTS):
            worker = rng.choice(qualified)
            duration = self._sample_duration(problem, worker, window_minutes, grid, rng)
            if duration is None:
                continue
            slack = window_minutes - lead_in - duration
            if slack < 0:
                continue
            offset = lead_in + rng.randrange(slack // grid + 1) * grid
            start = window_start + timedelta(minutes=offset)
            end = start + timedelta(minutes=duration)
            availability = [window.interval for window in worker.available_windows]
            if minutes_inside(start, end, availability) != duration:
                continue
            if any(
                shift.worker_id == worker.worker_id
                and overlaps(start, end, shift.start, shift.end)
                for shift in existing
            ):
                continue
            return PlannedShift(
                shift_id=derive_uuid(individual_id, "shift", ordinal),
                worker_id=worker.worker_id,
                job_id=job_id,
                start=start,
                end=end,
            )
        return None

    @staticmethod
    def _sample_duration(
        problem: SchedulingProblem,
        worker: WorkerInfo,
        window_minutes: int,
        grid: int,
        rng: random.Random,
    ) -> int | None:
        minimum, maximum = effective_bounds(worker, problem.shifts)
        low = max(grid, -(-minimum // grid) * grid)
        high = min(maximum, (window_minutes // grid) * grid)
        if high < low:
            return None
        steps = (high - low) // grid + 1
        return low + rng.randrange(steps) * grid
