from __future__ import annotations

from dataclasses import replace
from uuid import UUID, uuid4

import pytest

from scheduler_api.engine.controller import GeneticAlgorithmController
from scheduler_api.engine.exceptions import (
    DuplicateInvocationError,
    DuplicateScoreError,
    InvalidPhaseResultError,
    MissingScorerOutputError,
    PopulationSizeMismatchError,
    StalePhaseResultError,
    UnknownExecutionError,
)
from scheduler_api.engine.execution.runner import TypedComponentRunner
from scheduler_api.engine.models.assignment import Individual
from scheduler_api.engine.models.component_io import (
    CullResult,
    MutateResult,
    ScoreResult,
    ScoreUpdate,
    SeedResult,
    SelectResult,
    StopResult,
)
from scheduler_api.engine.models.execution import (
    ExecutionState,
    ExecutionStatus,
    FailureInfo,
)
from scheduler_api.engine.models.phase import (
    ComponentCategory,
    PhaseResult,
    PhaseType,
)
from scheduler_api.engine.models.population import Population
from scheduler_api.engine.models.results import ExecutionResult
from scheduler_api.engine.solver import (
    MutatorBinding,
    ScorerBinding,
    StopperBinding,
    build_mvp_solver,
)

from .factories import make_assignment, make_job, make_problem


class EmptyingMutator:
    component_category = ComponentCategory.MUTATOR

    def mutate(self, input):
        return MutateResult(
            category="mutator",
            offspring=Population(
                individuals=tuple(
                    Individual(id=uuid4(), assignments=())
                    for _ in range(input.offspring_count)
                )
            ),
        )


class UnqualifiedMutator:
    component_category = ComponentCategory.MUTATOR

    def mutate(self, input):
        job_id = input.problem.jobs[-1].job_id
        return MutateResult(
            category="mutator",
            offspring=Population(
                individuals=tuple(
                    Individual(
                        id=uuid4(),
                        assignments=(
                            make_assignment(
                                worker_id=1,
                                job_id=job_id.int,
                                slot_index=0,
                            ),
                        ),
                    )
                    for _ in range(input.offspring_count)
                )
            ),
        )


class ConstantScorer:
    component_category = ComponentCategory.SCORER

    def __init__(self, score: float):
        self._score = score

    def score(self, input):
        return ScoreResult(
            category="scorer",
            updates=tuple(
                ScoreUpdate(individual_id=individual.id, score=self._score)
                for individual in input.population.individuals
            ),
        )


class ConstantStopper:
    component_category = ComponentCategory.STOPPER

    def __init__(self, reason: str):
        self._reason = reason

    def should_stop(self, input):
        return StopResult(
            category="stopper",
            should_stop=True,
            reason=self._reason,
        )


def make_custom_controller(mutator, *, problem=None, elitism_count=0):
    solver = build_mvp_solver(
        population_size=4,
        max_generations=2,
        random_seed=7,
        elitism_count=elitism_count,
    )
    solver = replace(
        solver,
        mutators=(MutatorBinding("custom_mutator", mutator, 1),),
    )
    controller = solver.create_controller(problem or make_problem())
    runner = TypedComponentRunner(solver.build_registry())
    return controller, runner


def make_controller(
    *,
    population_size: int = 4,
    max_generations: int = 2,
    random_seed: int = 7,
    elitism_count: int = 1,
) -> tuple[GeneticAlgorithmController, TypedComponentRunner]:
    solver = build_mvp_solver(
        population_size=population_size,
        max_generations=max_generations,
        random_seed=random_seed,
        elitism_count=elitism_count,
    )
    controller = solver.create_controller(make_problem())
    runner = TypedComponentRunner(solver.build_registry())
    return controller, runner


def run_plan(
    controller: GeneticAlgorithmController,
    runner: TypedComponentRunner,
    plan,
) -> PhaseResult:
    results = tuple(runner.run(invocation) for invocation in plan.invocations)
    return PhaseResult(
        execution_id=plan.execution_id,
        phase_execution_id=plan.phase_execution_id,
        results=results,
    )


def drive(
    controller: GeneticAlgorithmController,
    runner: TypedComponentRunner,
    execution_id: UUID,
) -> list[PhaseType]:
    phases: list[PhaseType] = []
    plan = controller.start(execution_id)
    while plan is not None:
        phases.append(plan.phase)
        result = run_plan(controller, runner, plan)
        plan = controller.complete_phase(plan, result)
        state = controller.get_state(execution_id)
        assert ExecutionState.model_validate(state.model_dump()) == state
    return phases


def advance_to_phase(
    controller: GeneticAlgorithmController,
    runner: TypedComponentRunner,
    execution_id: UUID,
    target: PhaseType,
):
    plan = controller.start(execution_id)
    assert plan is not None
    while plan.phase is not target:
        plan = controller.complete_phase(plan, run_plan(controller, runner, plan))
        assert plan is not None
    return plan


def replace_first_result(result: PhaseResult, payload) -> PhaseResult:
    first = result.results[0].model_copy(update={"result": payload})
    return PhaseResult(
        execution_id=result.execution_id,
        phase_execution_id=result.phase_execution_id,
        results=(first,) + result.results[1:],
    )


def test_controller_runs_full_generation_order():
    controller, runner = make_controller(max_generations=2)

    phases = drive(controller, runner, UUID(int=1))

    assert phases == [
        PhaseType.SEED,
        PhaseType.SCORE,
        PhaseType.SELECT,
        PhaseType.MUTATE,
        PhaseType.SCORE,
        PhaseType.CULL,
        PhaseType.CHECK_STOP,
        PhaseType.SELECT,
        PhaseType.MUTATE,
        PhaseType.SCORE,
        PhaseType.CULL,
        PhaseType.CHECK_STOP,
    ]
    result = controller.get_result(UUID(int=1))
    assert result.status is ExecutionStatus.COMPLETED
    assert result.generation == 2
    assert result.termination_reason == "generation_limit:2"
    assert result.best_individual is not None
    assert result.best_feasible is True
    assert result.best_total_score is not None
    assert result.failure is None


def test_controller_tracks_best_and_all_scorer_outputs():
    controller, runner = make_controller()
    execution_id = UUID(int=2)
    plan = controller.start(execution_id)

    plan = controller.complete_phase(plan, run_plan(controller, runner, plan))
    assert plan is not None
    assert plan.phase is PhaseType.SCORE
    controller.complete_phase(plan, run_plan(controller, runner, plan))

    state = controller.get_state(execution_id)
    assert state.best_individual is not None
    assert state.best_total_score is not None
    assert set(state.best_individual.scores) == {
        "skills_match",
        "worker_overlap",
        "coverage",
        "shift_length",
    }
    assert len(state.elite_individuals) == 1
    assert state.elite_individuals[0].id == state.best_individual.id


def test_controller_start_is_idempotent_while_running():
    controller, _ = make_controller()

    first = controller.start(UUID(int=3))
    second = controller.start(UUID(int=3))

    assert first is not None
    assert second is first


def test_controller_start_returns_none_when_terminal():
    controller, runner = make_controller(max_generations=1)
    execution_id = UUID(int=4)

    drive(controller, runner, execution_id)

    assert controller.start(execution_id) is None


def test_complete_phase_replay_returns_stored_plan_without_mutation():
    controller, runner = make_controller()
    execution_id = UUID(int=5)
    plan = controller.start(execution_id)
    result = run_plan(controller, runner, plan)
    next_plan = controller.complete_phase(plan, result)
    state_before = controller.get_state(execution_id).model_dump()

    replay_next = controller.complete_phase(plan, result)

    assert replay_next is next_plan
    assert controller.get_state(execution_id).model_dump() == state_before


def test_stale_plan_is_rejected():
    controller, runner = make_controller()
    execution_id = UUID(int=6)
    plan = controller.start(execution_id)
    controller.complete_phase(plan, run_plan(controller, runner, plan))

    stale_plan = plan.model_copy(update={"phase_execution_id": uuid4()})
    stale_result = PhaseResult(
        execution_id=stale_plan.execution_id,
        phase_execution_id=stale_plan.phase_execution_id,
        results=(run_plan(controller, runner, plan).results[0],),
    )

    with pytest.raises(StalePhaseResultError):
        controller.complete_phase(stale_plan, stale_result)


def test_duplicate_invocation_results_are_rejected():
    controller, runner = make_controller()
    plan = controller.start(UUID(int=7))
    result = run_plan(controller, runner, plan)

    duplicate = PhaseResult(
        execution_id=result.execution_id,
        phase_execution_id=result.phase_execution_id,
        results=(result.results[0], result.results[0]),
    )

    with pytest.raises(DuplicateInvocationError):
        controller.complete_phase(plan, duplicate)


def test_missing_invocation_results_are_rejected():
    controller, runner = make_controller()
    execution_id = UUID(int=8)
    seed_plan = controller.start(execution_id)
    score_plan = controller.complete_phase(
        seed_plan, run_plan(controller, runner, seed_plan)
    )
    assert score_plan is not None
    score_result = run_plan(controller, runner, score_plan)

    incomplete = PhaseResult(
        execution_id=score_result.execution_id,
        phase_execution_id=score_result.phase_execution_id,
        results=score_result.results[:-1],
    )

    with pytest.raises(InvalidPhaseResultError):
        controller.complete_phase(score_plan, incomplete)


def test_unknown_and_mismatched_results_are_rejected():
    controller, runner = make_controller()
    plan = controller.start(UUID(int=9))
    result = run_plan(controller, runner, plan)

    unknown_entry = result.results[0].model_copy(update={"invocation_id": uuid4()})
    unknown = PhaseResult(
        execution_id=result.execution_id,
        phase_execution_id=result.phase_execution_id,
        results=(unknown_entry,),
    )
    with pytest.raises(InvalidPhaseResultError):
        controller.complete_phase(plan, unknown)

    mismatched_entry = result.results[0].model_copy(update={"component_id": "other"})
    mismatched = PhaseResult(
        execution_id=result.execution_id,
        phase_execution_id=result.phase_execution_id,
        results=(mismatched_entry,),
    )
    with pytest.raises(InvalidPhaseResultError):
        controller.complete_phase(plan, mismatched)


def test_fail_marks_execution_failed_and_result_exposes_failure():
    controller, _ = make_controller()
    execution_id = UUID(int=10)
    controller.start(execution_id)
    failure = FailureInfo(
        error_type="RuntimeError",
        message="boom",
        phase=PhaseType.SEED,
        component_id="random_schedule",
    )

    controller.fail(execution_id, failure)

    state = controller.get_state(execution_id)
    assert state.status is ExecutionStatus.FAILED
    assert state.failure == failure
    assert controller.start(execution_id) is None
    result = controller.get_result(execution_id)
    assert isinstance(result, ExecutionResult)
    assert result.status is ExecutionStatus.FAILED
    assert result.failure == failure


def test_unknown_execution_is_rejected():
    controller, _ = make_controller()

    with pytest.raises(UnknownExecutionError):
        controller.get_state(UUID(int=11))


def test_same_seed_and_problem_produce_identical_best_individual():
    first_controller, first_runner = make_controller(random_seed=99)
    second_controller, second_runner = make_controller(random_seed=99)
    execution_id = UUID(int=12)

    drive(first_controller, first_runner, execution_id)
    drive(second_controller, second_runner, execution_id)

    first = first_controller.get_result(execution_id)
    second = second_controller.get_result(execution_id)
    assert first.best_individual is not None
    assert first.best_individual == second.best_individual
    assert first.best_total_score == second.best_total_score


def test_single_generation_stops_after_first_cull():
    controller, runner = make_controller(max_generations=1)

    phases = drive(controller, runner, UUID(int=13))

    assert phases[-2:] == [PhaseType.CULL, PhaseType.CHECK_STOP]
    result = controller.get_result(UUID(int=13))
    assert result.status is ExecutionStatus.COMPLETED
    assert result.generation == 1


def test_elitism_zero_keeps_previous_best_against_degrading_offspring():
    controller, runner = make_custom_controller(EmptyingMutator())
    execution_id = UUID(int=20)

    drive(controller, runner, execution_id)

    result = controller.get_result(execution_id)
    assert result.best_individual is not None
    assert len(result.best_individual.assignments) == 4
    assert result.best_total_score == 2.0
    assert result.best_feasible is True
    state = controller.get_state(execution_id)
    assert (
        max(
            individual.scores["coverage"] for individual in state.population.individuals
        )
        == 1.0
    )


def test_elitism_zero_keeps_feasible_best_against_infeasible_offspring():
    problem = make_problem(jobs=(make_job(11), make_job(12)))
    controller, runner = make_custom_controller(UnqualifiedMutator(), problem=problem)
    execution_id = UUID(int=21)

    drive(controller, runner, execution_id)

    result = controller.get_result(execution_id)
    assert result.best_individual is not None
    assert result.best_feasible is True
    assert result.best_individual.violations == ()
    assert result.best_total_score == 2.0
    state = controller.get_state(execution_id)
    assert all(individual.feasible for individual in state.population.individuals)


def test_multiple_scorers_aggregate_in_spec_order():
    solver = build_mvp_solver(population_size=4, max_generations=1, random_seed=7)
    solver = replace(
        solver,
        scorers=(
            ScorerBinding("first_scorer", ConstantScorer(0.2), 0.25),
            ScorerBinding("second_scorer", ConstantScorer(0.8), 0.75),
        ),
    )
    controller = solver.create_controller(make_problem())
    runner = TypedComponentRunner(solver.build_registry())
    execution_id = UUID(int=22)

    plan = controller.start(execution_id)
    plan = controller.complete_phase(plan, run_plan(controller, runner, plan))
    controller.complete_phase(plan, run_plan(controller, runner, plan))

    state = controller.get_state(execution_id)
    individual = state.population.individuals[0]
    assert list(individual.scores) == ["first_scorer", "second_scorer"]
    assert individual.scores == {"first_scorer": 0.2, "second_scorer": 0.8}
    assert state.best_total_score == pytest.approx(0.65)


def test_duplicate_scorer_output_is_rejected():
    controller, runner = make_controller()
    execution_id = UUID(int=23)
    seed_plan = controller.start(execution_id)
    score_plan = controller.complete_phase(
        seed_plan, run_plan(controller, runner, seed_plan)
    )
    result = run_plan(controller, runner, score_plan)
    first = result.results[0].result
    assert isinstance(first, ScoreResult)

    malformed = replace_first_result(
        result,
        ScoreResult(
            category="scorer",
            updates=(first.updates[0], first.updates[0]),
        ),
    )

    with pytest.raises(DuplicateScoreError):
        controller.complete_phase(score_plan, malformed)


def test_missing_scorer_output_is_rejected():
    controller, runner = make_controller()
    execution_id = UUID(int=24)
    seed_plan = controller.start(execution_id)
    score_plan = controller.complete_phase(
        seed_plan, run_plan(controller, runner, seed_plan)
    )
    result = run_plan(controller, runner, score_plan)

    malformed = replace_first_result(
        result,
        ScoreResult(category="scorer", updates=()),
    )

    with pytest.raises(MissingScorerOutputError):
        controller.complete_phase(score_plan, malformed)


def test_seed_result_size_mismatch_is_rejected():
    controller, runner = make_controller()
    plan = controller.start(UUID(int=25))
    result = run_plan(controller, runner, plan)

    malformed = replace_first_result(
        result,
        SeedResult(
            category="seeder",
            population=Population(individuals=()),
        ),
    )

    with pytest.raises(PopulationSizeMismatchError):
        controller.complete_phase(plan, malformed)


def test_select_result_size_mismatch_is_rejected():
    controller, runner = make_controller()
    execution_id = UUID(int=26)
    plan = advance_to_phase(controller, runner, execution_id, PhaseType.SELECT)
    result = run_plan(controller, runner, plan)
    selected = result.results[0].result
    assert isinstance(selected, SelectResult)

    malformed = replace_first_result(
        result,
        SelectResult(
            category="selector",
            selected=Population(individuals=selected.selected.individuals[:-1]),
        ),
    )

    with pytest.raises(PopulationSizeMismatchError):
        controller.complete_phase(plan, malformed)


def test_mutate_result_size_mismatch_is_rejected():
    controller, runner = make_controller()
    execution_id = UUID(int=27)
    plan = advance_to_phase(controller, runner, execution_id, PhaseType.MUTATE)
    result = run_plan(controller, runner, plan)
    mutated = result.results[0].result
    assert isinstance(mutated, MutateResult)

    malformed = replace_first_result(
        result,
        MutateResult(
            category="mutator",
            offspring=Population(individuals=mutated.offspring.individuals[:-1]),
        ),
    )

    with pytest.raises(PopulationSizeMismatchError):
        controller.complete_phase(plan, malformed)


def test_cull_result_size_mismatch_is_rejected():
    controller, runner = make_controller()
    execution_id = UUID(int=28)
    plan = advance_to_phase(controller, runner, execution_id, PhaseType.CULL)
    result = run_plan(controller, runner, plan)
    retained = result.results[0].result
    assert isinstance(retained, CullResult)

    malformed = replace_first_result(
        result,
        CullResult(
            category="culler",
            population=Population(individuals=retained.population.individuals[:-1]),
        ),
    )

    with pytest.raises(PopulationSizeMismatchError):
        controller.complete_phase(plan, malformed)


def test_cull_must_keep_every_elite():
    controller, runner = make_controller()
    execution_id = UUID(int=29)
    plan = advance_to_phase(controller, runner, execution_id, PhaseType.CULL)
    result = run_plan(controller, runner, plan)
    state = controller.get_state(execution_id)
    retained = result.results[0].result
    assert isinstance(retained, CullResult)
    assert state.offspring is not None

    elite_id = state.elite_individuals[0].id
    retained_ids = {individual.id for individual in retained.population.individuals}
    assert elite_id in retained_ids
    candidates = state.population.individuals + state.offspring.individuals
    replacement = next(
        individual for individual in candidates if individual.id not in retained_ids
    )
    dropped = tuple(
        replacement if individual.id == elite_id else individual
        for individual in retained.population.individuals
    )

    malformed = replace_first_result(
        result,
        CullResult(
            category="culler",
            population=Population(individuals=dropped),
        ),
    )

    with pytest.raises(InvalidPhaseResultError, match="elite"):
        controller.complete_phase(plan, malformed)


def test_first_stopping_stopper_reason_wins():
    solver = build_mvp_solver(population_size=2, max_generations=1)
    solver = replace(
        solver,
        stoppers=(
            StopperBinding("first_stopper", ConstantStopper("first")),
            StopperBinding("second_stopper", ConstantStopper("second")),
        ),
    )
    controller = solver.create_controller(make_problem())
    runner = TypedComponentRunner(solver.build_registry())
    execution_id = UUID(int=30)

    drive(controller, runner, execution_id)

    assert controller.get_result(execution_id).termination_reason == "first"


def test_fail_is_a_no_op_without_state():
    controller, _ = make_controller()
    failure = FailureInfo(error_type="RuntimeError", message="boom")

    controller.fail(UUID(int=31), failure)

    with pytest.raises(UnknownExecutionError):
        controller.get_state(UUID(int=31))


def test_fail_is_a_no_op_for_terminal_execution():
    controller, runner = make_controller(max_generations=1)
    execution_id = UUID(int=32)
    drive(controller, runner, execution_id)
    before = controller.get_result(execution_id)
    failure = FailureInfo(error_type="RuntimeError", message="late failure")

    controller.fail(execution_id, failure)

    after = controller.get_result(execution_id)
    assert after.status is ExecutionStatus.COMPLETED
    assert after.failure is None
    assert after == before
