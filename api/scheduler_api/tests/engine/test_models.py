from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import get_args
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest
from pydantic import TypeAdapter, ValidationError

from scheduler_api.engine.models.assignment import Assignment, Individual
from scheduler_api.engine.models.component_io import (
    ComponentInputPayload,
    ComponentResultPayload,
    CullInput,
    CullResult,
    MutateInput,
    MutateResult,
    ScoreInput,
    ScoreResult,
    SeedInput,
    SeedResult,
    SelectInput,
    SelectResult,
    StopInput,
    StopResult,
)
from scheduler_api.engine.models.execution import (
    ExecutionState,
    ExecutionStatus,
)
from scheduler_api.engine.models.phase import (
    PHASE_CATEGORY,
    ComponentCategory,
    ComponentInvocation,
    ComponentResult,
    PhasePlan,
    PhaseResult,
    PhaseType,
)
from scheduler_api.engine.models.population import Population
from scheduler_api.engine.models.problem import (
    JobInfo,
    SchedulingProblem,
    StaffingRequirement,
    TimeSlot,
    WorkerInfo,
)
from scheduler_api.engine.models.scores import ScorerWeight, ScoringPolicy
from scheduler_api.engine.models.solver_spec import (
    MutatorPlan,
    SeederContribution,
    SolverSpec,
)

UTC = timezone.utc


def make_slots(count: int = 4) -> tuple[TimeSlot, ...]:
    start = datetime(2026, 1, 1, 8, 0, tzinfo=UTC)
    return tuple(
        TimeSlot(
            index=index,
            start=start + timedelta(minutes=15 * index),
            end=start + timedelta(minutes=15 * (index + 1)),
        )
        for index in range(count)
    )


def make_problem() -> SchedulingProblem:
    worker_id = UUID(int=1)
    job_id = UUID(int=11)
    return SchedulingProblem(
        timezone="UTC",
        slots=make_slots(),
        staffing_requirements=tuple(
            StaffingRequirement(
                job_id=job_id,
                slot_index=index,
                required_workers=1,
            )
            for index in range(4)
        ),
        workers=(
            WorkerInfo(
                worker_id=worker_id,
                available_slot_indices=(0, 1, 2, 3),
                qualified_job_ids=(job_id,),
            ),
        ),
        jobs=(JobInfo(job_id=job_id),),
    )


def make_assignment(worker: int = 1, job: int = 11, slot: int = 0) -> Assignment:
    return Assignment(
        worker_id=UUID(int=worker),
        job_id=UUID(int=job),
        slot_index=slot,
    )


def test_time_slot_requires_timezone_aware_datetimes():
    with pytest.raises(ValidationError):
        TimeSlot(
            index=0,
            start=datetime(2026, 1, 1, 8, 0),
            end=datetime(2026, 1, 1, 8, 15),
        )


def test_time_slot_requires_positive_duration():
    with pytest.raises(ValidationError):
        TimeSlot(
            index=0,
            start=datetime(2026, 1, 1, 8, 15, tzinfo=UTC),
            end=datetime(2026, 1, 1, 8, 0, tzinfo=UTC),
        )


def test_worker_info_normalizes_collections():
    job_a = UUID(int=2)
    job_b = UUID(int=1)
    worker = WorkerInfo(
        worker_id=UUID(int=1),
        available_slot_indices=(3, 1, 3, 0),
        qualified_job_ids=(job_a, job_b, job_a),
    )

    assert worker.available_slot_indices == (0, 1, 3)
    assert tuple(job.hex for job in worker.qualified_job_ids) == tuple(
        sorted((job_a.hex, job_b.hex))
    )


def test_problem_slot_count_and_validity():
    problem = make_problem()

    assert problem.slot_count == 4


def test_problem_rejects_non_contiguous_slots():
    slots = list(make_slots())
    slots[1] = slots[1].model_copy(
        update={"start": slots[1].start + timedelta(minutes=1)}
    )

    with pytest.raises(ValidationError, match="contiguous"):
        SchedulingProblem(
            timezone="UTC",
            slots=tuple(slots),
            staffing_requirements=(),
            workers=(),
            jobs=(),
        )


def test_problem_rejects_unknown_demand_references():
    job_id = UUID(int=11)
    with pytest.raises(ValidationError, match="unknown job"):
        SchedulingProblem(
            timezone="UTC",
            slots=make_slots(),
            staffing_requirements=(
                StaffingRequirement(
                    job_id=job_id,
                    slot_index=0,
                    required_workers=1,
                ),
            ),
            workers=(),
            jobs=(),
        )


def test_problem_rejects_duplicate_demand():
    job_id = UUID(int=11)
    requirement = StaffingRequirement(
        job_id=job_id,
        slot_index=0,
        required_workers=1,
    )

    with pytest.raises(ValidationError, match="duplicate staffing"):
        SchedulingProblem(
            timezone="UTC",
            slots=make_slots(),
            staffing_requirements=(requirement, requirement),
            workers=(),
            jobs=(JobInfo(job_id=job_id),),
        )


def test_problem_rejects_worker_availability_out_of_range():
    job_id = UUID(int=11)
    with pytest.raises(ValidationError, match="unknown slot"):
        SchedulingProblem(
            timezone="UTC",
            slots=make_slots(),
            staffing_requirements=(),
            workers=(
                WorkerInfo(
                    worker_id=UUID(int=1),
                    available_slot_indices=(4,),
                    qualified_job_ids=(job_id,),
                ),
            ),
            jobs=(JobInfo(job_id=job_id),),
        )


def test_individual_canonicalizes_assignments():
    individual = Individual(
        id=UUID(int=100),
        assignments=(
            make_assignment(slot=2),
            make_assignment(slot=0),
            make_assignment(slot=1),
        ),
    )

    assert [item.slot_index for item in individual.assignments] == [0, 1, 2]
    assert individual.feasible


def test_individual_rejects_duplicate_assignments():
    assignment = make_assignment()

    with pytest.raises(ValidationError, match="duplicate assignments"):
        Individual(id=UUID(int=100), assignments=(assignment, assignment))


def test_individual_scores_must_be_finite():
    with pytest.raises(ValidationError):
        Individual(
            id=UUID(int=100),
            assignments=(),
            scores={"coverage": float("nan")},
        )


def test_population_rejects_duplicate_individual_ids():
    individual = Individual(id=UUID(int=100), assignments=())

    with pytest.raises(ValidationError, match="duplicate individual IDs"):
        Population(individuals=(individual, individual))


def test_frozen_models_reject_mutation():
    individual = Individual(id=UUID(int=100), assignments=())

    with pytest.raises(ValidationError):
        individual.id = UUID(int=101)


def make_policy() -> ScoringPolicy:
    return ScoringPolicy(
        weights=(
            ScorerWeight(component_id="coverage", weight=1.0),
            ScorerWeight(component_id="shift_length", weight=0.5),
        )
    )


def make_component_payloads() -> tuple[ComponentInputPayload, ...]:
    problem = make_problem()
    population = Population(individuals=())
    policy = make_policy()
    return (
        SeedInput(
            category="seeder",
            problem=problem,
            population_size=3,
            rng_seed=7,
        ),
        ScoreInput(category="scorer", problem=problem, population=population),
        SelectInput(
            category="selector",
            population=population,
            count=0,
            scoring_policy=policy,
        ),
        MutateInput(
            category="mutator",
            problem=problem,
            parents=population,
            offspring_count=0,
            rng_seed=3,
        ),
        CullInput(
            category="culler",
            population=population,
            target_size=1,
            scoring_policy=policy,
        ),
        StopInput(
            category="stopper",
            execution_id=UUID(int=1),
            generation=0,
            population_size=0,
        ),
    )


def make_component_results() -> tuple[ComponentResultPayload, ...]:
    population = Population(individuals=())
    return (
        SeedResult(category="seeder", population=population),
        ScoreResult(category="scorer", updates=()),
        SelectResult(category="selector", selected=population),
        MutateResult(category="mutator", offspring=population),
        CullResult(category="culler", population=population),
        StopResult(category="stopper", should_stop=False),
    )


def test_component_payload_union_accepts_every_category():
    adapter = TypeAdapter(ComponentInputPayload)

    for payload in make_component_payloads():
        restored = adapter.validate_python(adapter.dump_python(payload, mode="json"))
        assert type(restored) is type(payload)


def test_component_result_union_accepts_every_category():
    adapter = TypeAdapter(ComponentResultPayload)

    for result in make_component_results():
        restored = adapter.validate_python(adapter.dump_python(result, mode="json"))
        assert type(restored) is type(result)


def test_category_literals_match_component_category_enum():
    payload_classes = (
        SeedInput,
        ScoreInput,
        SelectInput,
        MutateInput,
        CullInput,
        StopInput,
        SeedResult,
        ScoreResult,
        SelectResult,
        MutateResult,
        CullResult,
        StopResult,
    )

    literals = {
        get_args(cls.model_fields["category"].annotation)[0] for cls in payload_classes
    }

    assert literals == {category.value for category in ComponentCategory}


@pytest.mark.parametrize(
    ("phase", "payload", "payload_result"),
    list(zip(PhaseType, make_component_payloads(), make_component_results())),
    ids=[phase.value for phase in PhaseType],
)
def test_phase_plan_and_result_json_round_trip(
    phase: PhaseType,
    payload: ComponentInputPayload,
    payload_result: ComponentResultPayload,
):
    category = PHASE_CATEGORY[phase]
    invocation = ComponentInvocation(
        invocation_id=UUID(int=1),
        component_id=f"{category.value}_component",
        category=category,
        input=payload,
    )
    plan = PhasePlan(
        execution_id=UUID(int=2),
        phase_execution_id=UUID(int=3),
        generation=0,
        phase=phase,
        invocations=(invocation,),
    )

    restored_plan = PhasePlan.model_validate_json(plan.model_dump_json())
    assert restored_plan == plan

    result = ComponentResult(
        invocation_id=UUID(int=1),
        component_id=f"{category.value}_component",
        category=category,
        result=payload_result,
    )
    phase_result = PhaseResult(
        execution_id=UUID(int=2),
        phase_execution_id=UUID(int=3),
        results=(result,),
    )

    restored_result = PhaseResult.model_validate_json(phase_result.model_dump_json())
    assert restored_result == phase_result


@pytest.mark.parametrize(
    "payload",
    (make_component_payloads()[0], make_component_payloads()[1]),
    ids=("seed", "score"),
)
def test_component_payloads_forbid_extra_fields(payload):
    data = payload.model_dump(mode="json")
    data["unexpected"] = "rejected"

    with pytest.raises(ValidationError, match="Extra inputs"):
        type(payload).model_validate(data)


@pytest.mark.parametrize(
    "payload_result",
    (make_component_results()[0], make_component_results()[5]),
    ids=("seed", "stop"),
)
def test_component_results_forbid_extra_fields(payload_result):
    data = payload_result.model_dump(mode="json")
    data["unexpected"] = "rejected"

    with pytest.raises(ValidationError, match="Extra inputs"):
        type(payload_result).model_validate(data)


def test_phase_plan_rejects_category_mismatch():
    payload = make_component_payloads()[1]
    invocation = ComponentInvocation(
        invocation_id=UUID(int=1),
        component_id="coverage",
        category=ComponentCategory.SCORER,
        input=payload,
    )

    with pytest.raises(ValidationError):
        PhasePlan(
            execution_id=UUID(int=2),
            phase_execution_id=UUID(int=3),
            generation=0,
            phase=PhaseType.SEED,
            invocations=(invocation,),
        )


def test_phase_plan_rejects_duplicate_invocations():
    payload = make_component_payloads()[0]
    invocation = ComponentInvocation(
        invocation_id=UUID(int=1),
        component_id="random_schedule",
        category=ComponentCategory.SEEDER,
        input=payload,
    )

    with pytest.raises(ValidationError, match="duplicate invocation"):
        PhasePlan(
            execution_id=UUID(int=2),
            phase_execution_id=UUID(int=3),
            generation=0,
            phase=PhaseType.SEED,
            invocations=(invocation, invocation),
        )


def make_solver_spec(**overrides) -> SolverSpec:
    values = {
        "population_size": 4,
        "random_seed": 0,
        "elitism_count": 1,
        "seeders": (SeederContribution(component_id="seed", contribution=4),),
        "scorer_ids": ("coverage", "shift_length"),
        "scoring_policy": make_policy(),
        "selector_id": "top_n",
        "mutators": (MutatorPlan(component_id="mutate", offspring_per_parent=1),),
        "culler_id": "top_n",
        "stopper_ids": ("generations",),
    }
    values.update(overrides)
    return SolverSpec(**values)


def test_solver_spec_accepts_valid_configuration():
    spec = make_solver_spec()

    assert spec.population_size == 4


def test_solver_spec_requires_contributions_to_match_population():
    with pytest.raises(ValidationError, match="contributions"):
        make_solver_spec(
            seeders=(SeederContribution(component_id="seed", contribution=3),)
        )


def test_solver_spec_requires_scorer_ids_to_match_weights():
    with pytest.raises(ValidationError, match="scorer_ids"):
        make_solver_spec(scorer_ids=("coverage",))


def test_solver_spec_requires_elitism_within_population():
    with pytest.raises(ValidationError, match="elitism_count"):
        make_solver_spec(elitism_count=5)


def test_execution_state_status_invariants():
    problem = make_problem()
    base = {
        "execution_id": UUID(int=1),
        "problem": problem,
        "population": Population(individuals=()),
    }

    assert ExecutionState(**base).status is ExecutionStatus.RUNNING

    with pytest.raises(ValidationError, match="termination reason"):
        ExecutionState(**base, status=ExecutionStatus.COMPLETED)

    with pytest.raises(ValidationError, match="failure info"):
        ExecutionState(**base, status=ExecutionStatus.FAILED)


def test_folded_time_slot_uses_instants_for_ordering():
    zone = ZoneInfo("America/New_York")
    start = datetime(2026, 11, 1, 5, 30, tzinfo=timezone.utc).astimezone(zone)
    end = datetime(2026, 11, 1, 6, 0, tzinfo=timezone.utc).astimezone(zone)

    slot = TimeSlot(index=0, start=start, end=end)

    assert slot.start.utcoffset() != slot.end.utcoffset()
    assert slot.end.timestamp() > slot.start.timestamp()


def test_adjacent_slots_are_contiguous_across_fold():
    zone = ZoneInfo("America/New_York")
    starts = (
        datetime(2026, 11, 1, 5, 30, tzinfo=timezone.utc),
        datetime(2026, 11, 1, 6, 0, tzinfo=timezone.utc),
    )
    slots = tuple(
        TimeSlot(
            index=index,
            start=start.astimezone(zone),
            end=(start + timedelta(minutes=30)).astimezone(zone),
        )
        for index, start in enumerate(starts)
    )

    problem = SchedulingProblem(
        timezone="America/New_York",
        slots=slots,
        staffing_requirements=(),
        workers=(),
        jobs=(),
    )

    assert problem.slot_count == 2
