from __future__ import annotations

from typing import cast
from uuid import UUID

from scheduler_api.engine.exceptions import (
    DuplicateIndividualError,
    DuplicateScoreError,
    InvalidComponentResultError,
    InvalidPhaseResultError,
    MissingScorerOutputError,
    PopulationSizeMismatchError,
)
from scheduler_api.engine.models.assignment import Individual
from scheduler_api.engine.models.component_io import (
    CullInput,
    CullResult,
    MutateInput,
    MutateResult,
    ScoreInput,
    ScoreResult,
    ScoreUpdate,
    SeedInput,
    SeedResult,
    SelectInput,
    SelectResult,
    StopInput,
    StopResult,
)
from scheduler_api.engine.models.phase import (
    ComponentInvocation,
    PhasePlan,
    PhaseResult,
)
from scheduler_api.engine.models.population import Population
from scheduler_api.engine.models.problem import SchedulingProblem
from scheduler_api.engine.models.scores import Violation
from scheduler_api.engine.validation import validate_individual_structure


def _result_map(result: PhaseResult) -> dict[UUID, object]:
    return {entry.invocation_id: entry.result for entry in result.results}


def _require_input(invocation: ComponentInvocation, expected: type) -> object:
    if not isinstance(invocation.input, expected):
        raise InvalidPhaseResultError(
            f"invocation {invocation.invocation_id} has unexpected input"
        )
    return invocation.input


def _require_result(result: object, expected: type) -> object:
    if not isinstance(result, expected):
        raise InvalidPhaseResultError(
            f"component result has unexpected type {type(result).__name__}"
        )
    return result


def aggregate_seed(
    plan: PhasePlan,
    result: PhaseResult,
    population_size: int,
    problem: SchedulingProblem,
) -> Population:
    results = _result_map(result)
    individuals: list[Individual] = []
    seen_ids: set[UUID] = set()

    for invocation in plan.invocations:
        seed_input = cast(SeedInput, _require_input(invocation, SeedInput))
        seed_result = cast(
            SeedResult,
            _require_result(results[invocation.invocation_id], SeedResult),
        )
        actual = len(seed_result.population.individuals)
        if actual != seed_input.population_size:
            raise PopulationSizeMismatchError(
                seed_input.population_size,
                actual,
                component_id=invocation.component_id,
            )
        for individual in seed_result.population.individuals:
            if individual.id in seen_ids:
                raise DuplicateIndividualError(
                    f"duplicate individual ID {individual.id}",
                    component_id=invocation.component_id,
                )
            seen_ids.add(individual.id)
            validate_individual_structure(individual, problem)
            individuals.append(individual)

    if len(individuals) != population_size:
        raise PopulationSizeMismatchError(population_size, len(individuals))
    return Population(individuals=tuple(individuals))


def aggregate_scores(
    plan: PhasePlan,
    result: PhaseResult,
    target: Population,
) -> Population:
    results = _result_map(result)
    target_ids = {individual.id for individual in target.individuals}
    updates: dict[tuple[UUID, str], ScoreUpdate] = {}

    for invocation in plan.invocations:
        cast(ScoreInput, _require_input(invocation, ScoreInput))
        score_result = cast(
            ScoreResult,
            _require_result(results[invocation.invocation_id], ScoreResult),
        )
        for update in score_result.updates:
            if update.individual_id not in target_ids:
                raise InvalidPhaseResultError(
                    f"scorer {invocation.component_id} returned a score for "
                    f"unknown individual {update.individual_id}"
                )
            key = (update.individual_id, invocation.component_id)
            if key in updates:
                raise DuplicateScoreError(update.individual_id, invocation.component_id)
            updates[key] = update

    scored: list[Individual] = []
    for individual in target.individuals:
        scores: dict[str, float] = {}
        violations: list[Violation] = []
        seen_violations: set[Violation] = set()
        for invocation in plan.invocations:
            key = (individual.id, invocation.component_id)
            if key not in updates:
                raise MissingScorerOutputError(individual.id, invocation.component_id)
            update = updates[key]
            scores[invocation.component_id] = update.score
            for violation in update.violations:
                if violation in seen_violations:
                    continue
                seen_violations.add(violation)
                violations.append(violation)

        scored.append(
            Individual(
                id=individual.id,
                assignments=individual.assignments,
                scores=scores,
                violations=tuple(violations),
            )
        )

    return Population(individuals=tuple(scored))


def aggregate_select(
    plan: PhasePlan,
    result: PhaseResult,
    source: Population,
) -> Population:
    if len(plan.invocations) != 1:
        raise InvalidPhaseResultError("select phase requires exactly one invocation")
    results = _result_map(result)
    invocation = plan.invocations[0]
    select_input = cast(SelectInput, _require_input(invocation, SelectInput))
    select_result = cast(
        SelectResult,
        _require_result(results[invocation.invocation_id], SelectResult),
    )

    selected = select_result.selected.individuals
    if len(selected) != select_input.count:
        raise PopulationSizeMismatchError(
            select_input.count,
            len(selected),
            component_id=invocation.component_id,
        )

    source_ids = {individual.id for individual in source.individuals}
    selected_ids: set[UUID] = set()
    for individual in selected:
        if individual.id not in source_ids:
            raise InvalidPhaseResultError(
                f"selector returned unknown individual {individual.id}"
            )
        if individual.id in selected_ids:
            raise InvalidPhaseResultError(
                f"selector returned duplicate individual {individual.id}"
            )
        selected_ids.add(individual.id)

    return Population(individuals=selected)


def aggregate_mutate(
    plan: PhasePlan,
    result: PhaseResult,
    parents: Population,
    problem: SchedulingProblem,
) -> Population:
    results = _result_map(result)
    parent_ids = {individual.id for individual in parents.individuals}
    offspring: list[Individual] = []
    seen_ids: set[UUID] = set()

    for invocation in plan.invocations:
        mutate_input = cast(MutateInput, _require_input(invocation, MutateInput))
        mutate_result = cast(
            MutateResult,
            _require_result(results[invocation.invocation_id], MutateResult),
        )
        actual = len(mutate_result.offspring.individuals)
        if actual != mutate_input.offspring_count:
            raise PopulationSizeMismatchError(
                mutate_input.offspring_count,
                actual,
                component_id=invocation.component_id,
            )
        for individual in mutate_result.offspring.individuals:
            if individual.scores or individual.violations:
                raise InvalidComponentResultError(
                    f"mutator {invocation.component_id} returned a scored " "offspring",
                    component_id=invocation.component_id,
                )
            if individual.id in seen_ids or individual.id in parent_ids:
                raise DuplicateIndividualError(
                    f"duplicate individual ID {individual.id}",
                    component_id=invocation.component_id,
                )
            seen_ids.add(individual.id)
            validate_individual_structure(individual, problem)
            offspring.append(individual)

    return Population(individuals=tuple(offspring))


def aggregate_cull(
    plan: PhasePlan,
    result: PhaseResult,
    candidates: Population,
    target_size: int,
    elite_individuals: tuple[Individual, ...],
) -> Population:
    if len(plan.invocations) != 1:
        raise InvalidPhaseResultError("cull phase requires exactly one invocation")
    results = _result_map(result)
    invocation = plan.invocations[0]
    cast(CullInput, _require_input(invocation, CullInput))
    cull_result = cast(
        CullResult,
        _require_result(results[invocation.invocation_id], CullResult),
    )

    retained = cull_result.population.individuals
    if len(retained) != target_size:
        raise PopulationSizeMismatchError(
            target_size,
            len(retained),
            component_id=invocation.component_id,
        )

    allowed_ids = {individual.id for individual in candidates.individuals} | {
        individual.id for individual in elite_individuals
    }
    retained_ids: set[UUID] = set()
    for individual in retained:
        if individual.id in retained_ids:
            raise InvalidPhaseResultError(
                f"culler returned duplicate individual {individual.id}"
            )
        if individual.id not in allowed_ids:
            raise InvalidPhaseResultError(
                f"culler returned unknown individual {individual.id}"
            )
        retained_ids.add(individual.id)

    for elite in elite_individuals:
        if elite.id not in retained_ids:
            raise InvalidPhaseResultError(f"culler dropped required elite {elite.id}")

    return Population(individuals=retained)


def aggregate_stop(
    plan: PhasePlan,
    result: PhaseResult,
) -> tuple[bool, str | None]:
    results = _result_map(result)
    should_stop = False
    reason: str | None = None

    for invocation in plan.invocations:
        cast(StopInput, _require_input(invocation, StopInput))
        stop_result = cast(
            StopResult,
            _require_result(results[invocation.invocation_id], StopResult),
        )
        if stop_result.should_stop:
            should_stop = True
            if reason is None:
                reason = stop_result.reason or "stopped"

    return should_stop, reason if should_stop else None
