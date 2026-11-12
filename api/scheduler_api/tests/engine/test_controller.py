"""Controller: phase sequencing, aggregation, feasibility, and idempotency."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from scheduler_api.engine.errors import (
    ExecutionStateError,
    PhaseResultError,
    ProblemValidationError,
)
from scheduler_api.engine.execution.runner import ComponentRunner
from scheduler_api.engine.execution.store import InMemoryExecutionStore
from scheduler_api.engine.models.execution import ExecutionState, ExecutionStatus
from scheduler_api.engine.models.fitness import FitnessConfig
from scheduler_api.engine.models.genome import Population
from scheduler_api.engine.models.phase import PhaseResult, PhaseType
from scheduler_api.engine.models.problem import ScheduleLimits
from scheduler_api.engine.solver import GeneticAlgorithmSolver
from scheduler_api.engine.controller import GAController
from scheduler_api.tests.engine.builders import (
    make_individual,
    make_problem,
    make_shift,
)
from scheduler_api.tests.engine.conftest import minimal_settings


def drive(controller, runner, execution_id, *, limit=50):
    """Run an execution phase by phase, returning the phase sequence."""
    trace: list[tuple[PhaseType, int]] = []
    plan = controller.start(execution_id)
    guard = 0
    while plan is not None:
        guard += 1
        assert guard < limit, "execution did not terminate"
        trace.append((plan.phase, plan.generation))
        results = tuple(
            runner.run(component_invocation)
            for component_invocation in plan.invocations
        )
        plan = controller.complete_phase(
            plan,
            PhaseResult(
                execution_id=plan.execution_id,
                phase_execution_id=plan.phase_execution_id,
                results=results,
            ),
        )
    return trace


def build(problem, settings=None, seed=5, execution_id=None):
    registry = __import__(
        "scheduler_api.engine.solver", fromlist=["build_default_registry"]
    ).build_default_registry()
    runner = ComponentRunner(registry)
    store = InMemoryExecutionStore()
    solver = GeneticAlgorithmSolver(
        registry=registry, settings=settings or minimal_settings()
    )
    controller = GAController(solver, runner, store)
    resolved = execution_id or uuid4()
    store.save_request(
        solver.build_request(execution_id=resolved, problem=problem, random_seed=seed)
    )
    return controller, runner, store, resolved


def test_phase_sequence_for_one_generation() -> None:
    controller, runner, store, execution_id = build(make_problem())
    trace = drive(controller, runner, execution_id)
    assert [phase for phase, _ in trace] == [
        PhaseType.SEED,
        PhaseType.SCORE,
        PhaseType.SELECT,
        PhaseType.MUTATE,
        PhaseType.SCORE,
        PhaseType.CULL,
        PhaseType.CHECK_STOP,
    ]


def test_phase_sequence_repeats_generations() -> None:
    controller, runner, store, execution_id = build(
        make_problem(), minimal_settings(maximum_generations=2)
    )
    trace = drive(controller, runner, execution_id)
    phases = [phase for phase, _ in trace]
    assert phases.count(PhaseType.CHECK_STOP) == 2
    assert phases.count(PhaseType.MUTATE) == 2
    assert {generation for _, generation in trace} == {0, 1}


def test_second_score_phase_scores_only_offspring() -> None:
    controller, runner, store, execution_id = build(make_problem())
    plan = controller.start(execution_id)
    first_score_ids: set[UUID] | None = None
    second_score_ids: set[UUID] | None = None
    seen_scores = 0
    while plan is not None:
        if plan.phase is PhaseType.SCORE:
            seen_scores += 1
            ids = {
                individual.id for individual in plan.invocations[0].input.individuals
            }
            if seen_scores == 1:
                first_score_ids = ids
            else:
                second_score_ids = ids
        results = tuple(
            runner.run(component_invocation)
            for component_invocation in plan.invocations
        )
        plan = controller.complete_phase(
            plan,
            PhaseResult(
                execution_id=plan.execution_id,
                phase_execution_id=plan.phase_execution_id,
                results=results,
            ),
        )
    assert first_score_ids is not None and second_score_ids is not None
    assert first_score_ids.isdisjoint(second_score_ids)
    state = store.load_state(execution_id)
    surviving = {individual.id for individual in state.population.individuals}
    assert surviving <= (first_score_ids | second_score_ids)


def test_fitness_is_the_weighted_mean_of_the_configured_scorers() -> None:
    settings = minimal_settings(fitness=FitnessConfig(weights={"coverage": 2.0}))
    controller, runner, store, execution_id = build(make_problem(), settings)
    drive(controller, runner, execution_id)
    state = store.load_state(execution_id)
    for individual in state.population.individuals:
        assert individual.fitness == pytest.approx(individual.scores["coverage"])


def test_zero_weight_scorers_do_not_enter_fitness() -> None:
    from scheduler_api.engine.models.config import (
        AvailabilityScorerConfig,
        CoverageScorerConfig,
    )

    settings = minimal_settings()
    settings = settings.model_copy(
        update={
            "scorers": (CoverageScorerConfig(), AvailabilityScorerConfig()),
            "fitness": FitnessConfig(weights={"coverage": 1.0, "availability": 0.0}),
        }
    )
    controller, runner, store, execution_id = build(make_problem(), settings)
    drive(controller, runner, execution_id)
    state = store.load_state(execution_id)
    for individual in state.population.individuals:
        assert "availability" in individual.scores
        assert individual.fitness == pytest.approx(individual.scores["coverage"])


def test_completing_a_phase_twice_is_idempotent() -> None:
    controller, runner, store, execution_id = build(make_problem())
    plan = controller.start(execution_id)
    results = tuple(
        runner.run(component_invocation) for component_invocation in plan.invocations
    )
    phase_result = PhaseResult(
        execution_id=plan.execution_id,
        phase_execution_id=plan.phase_execution_id,
        results=results,
    )
    next_plan = controller.complete_phase(plan, phase_result)
    population_after_first = store.load_state(execution_id).population
    replay_plan = controller.complete_phase(plan, phase_result)
    assert replay_plan == next_plan
    assert store.load_state(execution_id).population == population_after_first


def test_a_phase_result_for_another_phase_is_rejected() -> None:
    controller, runner, store, execution_id = build(make_problem())
    plan = controller.start(execution_id)
    results = tuple(
        runner.run(component_invocation) for component_invocation in plan.invocations
    )
    with pytest.raises(PhaseResultError):
        controller.complete_phase(
            plan,
            PhaseResult(
                execution_id=plan.execution_id,
                phase_execution_id=uuid4(),
                results=results,
            ),
        )


def test_a_phase_result_missing_an_invocation_is_rejected() -> None:
    from scheduler_api.engine.models.config import (
        AvailabilityScorerConfig,
        CoverageScorerConfig,
    )

    settings = minimal_settings()
    settings = settings.model_copy(
        update={"scorers": (CoverageScorerConfig(), AvailabilityScorerConfig())}
    )
    controller, runner, store, execution_id = build(make_problem(), settings)
    controller.start(execution_id)
    plan = controller.complete_phase  # appease linters; real use below
    seed_plan = store.load_state(execution_id).next_plan
    assert seed_plan is not None
    seed_results = tuple(
        runner.run(component_invocation)
        for component_invocation in seed_plan.invocations
    )
    score_plan = controller.complete_phase(
        seed_plan,
        PhaseResult(
            execution_id=seed_plan.execution_id,
            phase_execution_id=seed_plan.phase_execution_id,
            results=seed_results,
        ),
    )
    assert score_plan is not None
    partial = tuple(
        runner.run(component_invocation)
        for component_invocation in score_plan.invocations[:1]
    )
    with pytest.raises(PhaseResultError):
        controller.complete_phase(
            score_plan,
            PhaseResult(
                execution_id=score_plan.execution_id,
                phase_execution_id=score_plan.phase_execution_id,
                results=partial,
            ),
        )
    del plan


def test_all_infeasible_runs_return_infeasible_candidates() -> None:
    from scheduler_api.engine.models.config import (
        CoverageScorerConfig,
        ScheduleLimitsScorerConfig,
    )

    settings = minimal_settings().model_copy(
        update={
            "scorers": (CoverageScorerConfig(), ScheduleLimitsScorerConfig()),
            "fitness": FitnessConfig(weights={"coverage": 1.0, "schedule_limits": 0.0}),
        }
    )
    problem = make_problem(limits=ScheduleLimits(maximum_hours_per_week=1))
    controller, runner, store, execution_id = build(problem, settings)
    drive(controller, runner, execution_id)
    result = controller.result(execution_id)
    assert result.candidates
    assert all(candidate.feasible is False for candidate in result.candidates)
    assert all(candidate.violations for candidate in result.candidates)


def test_candidates_are_deduplicated_by_schedule_identity() -> None:
    controller, runner, store, execution_id = build(
        make_problem(), minimal_settings(max_candidates=3)
    )
    shifts = (make_shift(UUID(int=1), UUID(int=101), 8, 16),)
    clones = tuple(
        make_individual(shifts, individual_id=UUID(int=700 + index), fitness=50.0)
        for index in range(3)
    )
    distinct = make_individual(
        (make_shift(UUID(int=2), UUID(int=101), 8, 16),),
        individual_id=UUID(int=799),
        fitness=40.0,
    )
    request = store.load_request(execution_id)
    state = ExecutionState(
        execution_id=execution_id,
        status=ExecutionStatus.RUNNING,
        population=Population(individuals=(*clones, distinct)),
    )
    result = controller._finalize(state, request)
    assert len(result.candidates) == 2
    assert [candidate.rank for candidate in result.candidates] == [1, 2]


def test_start_rejects_an_invalid_problem() -> None:
    controller, runner, store, execution_id = build(make_problem(requirements=()))
    with pytest.raises(ProblemValidationError):
        controller.start(execution_id)


def test_result_is_unavailable_before_completion() -> None:
    controller, runner, store, execution_id = build(make_problem())
    with pytest.raises(ExecutionStateError):
        controller.result(execution_id)


def test_start_is_resumable() -> None:
    controller, runner, store, execution_id = build(make_problem())
    first = controller.start(execution_id)
    second = controller.start(execution_id)
    assert first == second


def test_scoring_target_is_cleared_after_scoring() -> None:
    controller, runner, store, execution_id = build(make_problem())
    drive(controller, runner, execution_id)
    state = store.load_state(execution_id)
    assert state.status is ExecutionStatus.COMPLETED
    assert state.scoring_target is None
    assert isinstance(state.population, Population)
