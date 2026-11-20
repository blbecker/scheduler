from __future__ import annotations

from uuid import UUID

from scheduler_api.engine.components.scorers.coverage import CoverageScorer
from scheduler_api.engine.components.scorers.overlap import WorkerOverlapScorer
from scheduler_api.engine.components.scorers.shift_length import (
    ShiftLengthScorer,
)
from scheduler_api.engine.components.scorers.skills_match import (
    SkillsMatchScorer,
)
from scheduler_api.engine.execution.local import LocalExecutor
from scheduler_api.engine.execution.runner import TypedComponentRunner
from scheduler_api.engine.models.assignment import Individual
from scheduler_api.engine.models.component_io import ScoreInput
from scheduler_api.engine.models.execution import ExecutionStatus
from scheduler_api.engine.models.population import Population
from scheduler_api.engine.models.scores import Violation, ViolationCode
from scheduler_api.engine.ranking import rank_individuals
from scheduler_api.engine.solver import build_mvp_solver
from scheduler_api.mappers.assignment_shift_mapper import coalesce_assignments

from .factories import (
    make_assignment,
    make_demand,
    make_individual,
    make_job,
    make_policy,
    make_problem,
    make_slots,
    make_worker,
)


def solve(problem, *, population_size=8, random_seed=7, max_generations=2):
    solver = build_mvp_solver(
        population_size=population_size,
        random_seed=random_seed,
        max_generations=max_generations,
    )
    controller = solver.create_controller(problem)
    executor = LocalExecutor(controller, TypedComponentRunner(solver.build_registry()))
    execution_id = UUID(int=42)
    executor.execute(execution_id)
    return controller, controller.get_result(execution_id)


def score_one(scorer, problem, individual):
    return scorer.score(
        ScoreInput(
            category="scorer",
            problem=problem,
            population=Population(individuals=(individual,)),
        )
    ).updates[0]


def test_fully_covered_solution_is_feasible_and_coalesces():
    problem = make_problem()

    controller, result = solve(problem)

    assert result.status is ExecutionStatus.COMPLETED
    assert result.best_individual is not None
    assert result.best_feasible is True
    assert result.best_individual.feasible is True
    assert result.best_individual.scores == {
        "skills_match": 1.0,
        "worker_overlap": 1.0,
        "coverage": 1.0,
        "shift_length": 1.0,
    }
    assert result.best_total_score == 2.0
    shifts = coalesce_assignments(problem, result.best_individual)
    assert len(shifts) == 1
    assert shifts[0].start.hour == 8
    assert shifts[0].end.hour == 9
    assert shifts[0].slot_indices == (0, 1, 2, 3)


def test_unavailable_worker_is_infeasible():
    problem = make_problem(workers=(make_worker(slot_indices=(0, 1)),))
    individual = make_individual(assignments=(make_assignment(slot_index=2),))

    update = score_one(SkillsMatchScorer(), problem, individual)

    assert update.score == 0.0
    assert ViolationCode.UNAVAILABLE_WORKER in {
        violation.code for violation in update.violations
    }
    scored = Individual(
        id=individual.id,
        assignments=individual.assignments,
        scores={"skills_match": update.score},
        violations=update.violations,
    )
    assert scored.feasible is False


def test_unqualified_worker_is_infeasible():
    problem = make_problem(
        jobs=(make_job(11), make_job(12)),
        workers=(make_worker(job_ids=(11,)),),
    )
    individual = make_individual(
        assignments=(make_assignment(job_id=12, slot_index=0),)
    )

    update = score_one(SkillsMatchScorer(), problem, individual)

    assert update.score == 0.0
    assert ViolationCode.UNQUALIFIED_WORKER in {
        violation.code for violation in update.violations
    }


def test_simultaneous_assignments_are_double_booked():
    problem = make_problem(
        jobs=(make_job(11), make_job(12)),
        workers=(make_worker(job_ids=(11, 12)),),
    )
    individual = make_individual(
        assignments=(
            make_assignment(job_id=11, slot_index=0),
            make_assignment(job_id=12, slot_index=0),
        )
    )

    update = score_one(WorkerOverlapScorer(), problem, individual)

    assert update.score == 0.5
    assert ViolationCode.WORKER_DOUBLE_BOOKED in {
        violation.code for violation in update.violations
    }


def test_understaffing_lowers_coverage_score():
    problem = make_problem(
        staffing_requirements=tuple(
            make_demand(slot_index=index, required_workers=2) for index in range(4)
        )
    )

    _, result = solve(problem)

    assert result.best_individual is not None
    assert result.best_individual.scores["coverage"] == 0.5
    assert result.best_total_score is not None
    assert result.best_total_score < 2.0


def test_overstaffing_lowers_coverage_score():
    problem = make_problem(workers=(make_worker(worker_id=1), make_worker(worker_id=2)))
    individual = make_individual(
        assignments=(
            make_assignment(worker_id=1, slot_index=0),
            make_assignment(worker_id=2, slot_index=0),
        )
    )

    update = score_one(CoverageScorer(), problem, individual)

    assert update.score == 0.0
    assert update.violations == ()


def test_shift_length_penalties_are_soft():
    problem = make_problem(
        slots=make_slots(6),
        workers=(make_worker(slot_indices=tuple(range(6)), minimum=2, maximum=3),),
        staffing_requirements=(),
    )
    individual = make_individual(
        assignments=tuple(
            make_assignment(slot_index=index) for index in (0, 2, 3, 4, 5)
        )
    )

    update = score_one(ShiftLengthScorer(), problem, individual)

    assert 0.0 < update.score < 1.0
    assert update.violations == ()


def test_feasible_individual_ranks_before_higher_scoring_infeasible():
    feasible = make_individual(individual_id=1, scores={"coverage": 0.1})
    infeasible = Individual(
        id=UUID(int=2),
        assignments=(),
        scores={"coverage": 1.0},
        violations=(
            Violation(
                code=ViolationCode.UNKNOWN_WORKER,
                message="broken",
            ),
        ),
    )

    ranked = rank_individuals((infeasible, feasible), make_policy(("coverage", 1.0)))

    assert ranked[0].id == feasible.id
    assert ranked[1].id == infeasible.id


def test_same_seed_produces_same_end_to_end_result():
    problem = make_problem()

    _, first = solve(problem, random_seed=123)
    _, second = solve(problem, random_seed=123)

    assert first.best_individual == second.best_individual
    assert first.best_total_score == second.best_total_score
