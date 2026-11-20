from __future__ import annotations

from uuid import UUID

import pytest

from scheduler_api.engine.aggregation import aggregate_cull, aggregate_select
from scheduler_api.engine.exceptions import InvalidPhaseResultError
from scheduler_api.engine.models.component_io import (
    CullInput,
    CullResult,
    SelectInput,
    SelectResult,
)
from scheduler_api.engine.models.phase import (
    ComponentCategory,
    ComponentInvocation,
    ComponentResult,
    PhasePlan,
    PhaseResult,
    PhaseType,
)
from scheduler_api.engine.models.population import Population

from .factories import make_individual, make_policy


def make_two_invocation_phase(phase, category, payload, payload_result):
    invocations = tuple(
        ComponentInvocation(
            invocation_id=UUID(int=index),
            component_id=f"{category.value}_{index}",
            category=category,
            input=payload,
        )
        for index in (1, 2)
    )
    plan = PhasePlan(
        execution_id=UUID(int=10),
        phase_execution_id=UUID(int=11),
        generation=0,
        phase=phase,
        invocations=invocations,
    )
    results = tuple(
        ComponentResult(
            invocation_id=invocation.invocation_id,
            component_id=invocation.component_id,
            category=category,
            result=payload_result,
        )
        for invocation in invocations
    )
    return plan, PhaseResult(
        execution_id=plan.execution_id,
        phase_execution_id=plan.phase_execution_id,
        results=results,
    )


def test_select_aggregation_rejects_multiple_invocations():
    population = Population(individuals=(make_individual(),))
    payload = SelectInput(
        category="selector",
        population=population,
        count=1,
        scoring_policy=make_policy(),
    )
    plan, result = make_two_invocation_phase(
        PhaseType.SELECT,
        ComponentCategory.SELECTOR,
        payload,
        SelectResult(category="selector", selected=population),
    )

    with pytest.raises(InvalidPhaseResultError, match="exactly one"):
        aggregate_select(plan, result, population)


def test_cull_aggregation_rejects_multiple_invocations():
    population = Population(individuals=(make_individual(),))
    payload = CullInput(
        category="culler",
        population=population,
        target_size=1,
        scoring_policy=make_policy(),
    )
    plan, result = make_two_invocation_phase(
        PhaseType.CULL,
        ComponentCategory.CULLER,
        payload,
        CullResult(category="culler", population=population),
    )

    with pytest.raises(InvalidPhaseResultError, match="exactly one"):
        aggregate_cull(
            plan,
            result,
            candidates=population,
            target_size=1,
            elite_individuals=(),
        )
