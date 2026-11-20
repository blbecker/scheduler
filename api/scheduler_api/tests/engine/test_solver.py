from __future__ import annotations

from dataclasses import replace

import pytest

from scheduler_api.engine.components.seeders.random import (
    RandomScheduleSeeder,
)
from scheduler_api.engine.exceptions import SolverConfigurationError
from scheduler_api.engine.models.phase import ComponentCategory
from scheduler_api.engine.solver import (
    ScorerBinding,
    SeederBinding,
    build_mvp_solver,
)


def test_mvp_solver_spec_matches_configuration():
    solver = build_mvp_solver(
        population_size=6,
        random_seed=3,
        max_generations=4,
        offspring_per_parent=2,
        elitism_count=2,
    )

    spec = solver.to_spec()

    assert spec.population_size == 6
    assert spec.random_seed == 3
    assert spec.elitism_count == 2
    assert spec.seeders[0].component_id == "random_schedule"
    assert spec.seeders[0].contribution == 6
    assert spec.scorer_ids == (
        "skills_match",
        "worker_overlap",
        "coverage",
        "shift_length",
    )
    assert spec.scoring_policy.weight_for("coverage") == 1.0
    assert spec.scoring_policy.weight_for("skills_match") == 0.0
    assert spec.selector_id == "top_n"
    assert spec.mutators[0].offspring_per_parent == 2
    assert spec.culler_id == "top_n"
    assert spec.stopper_ids == ("generation_count",)


def test_mvp_registry_resolves_every_component():
    registry = build_mvp_solver().build_registry()

    assert registry.resolve_seeder("random_schedule")
    assert registry.resolve_scorer("coverage")
    assert registry.resolve_selector("top_n")
    assert registry.resolve_mutator("random_replacement")
    assert registry.resolve_culler("top_n")
    assert registry.resolve_stopper("generation_count")


def test_spec_round_trips_through_json():
    spec = build_mvp_solver().to_spec()

    restored = type(spec).model_validate(spec.model_dump(mode="json"))

    assert restored == spec


def test_empty_seeders_are_rejected():
    with pytest.raises(SolverConfigurationError):
        replace(build_mvp_solver(), seeders=())


def test_seeder_contributions_must_sum_to_population_size():
    solver = build_mvp_solver(population_size=5)

    with pytest.raises(SolverConfigurationError):
        replace(
            solver,
            seeders=(SeederBinding("only", RandomScheduleSeeder(), 4),),
        )


def test_duplicate_component_ids_are_rejected():
    solver = build_mvp_solver()
    binding = ScorerBinding("duplicate", solver.scorers[0].component, 1.0)

    with pytest.raises(SolverConfigurationError):
        replace(solver, scorers=(binding, binding))


def test_elitism_above_population_is_rejected():
    with pytest.raises(SolverConfigurationError):
        build_mvp_solver(population_size=2, elitism_count=3)


def test_scorer_weight_above_one_is_rejected():
    solver = build_mvp_solver()
    binding = ScorerBinding(
        solver.scorers[0].component_id, solver.scorers[0].component, 2.0
    )

    with pytest.raises(SolverConfigurationError):
        replace(solver, scorers=(binding,))


def test_component_category_must_match_binding():
    class WrongCategorySeeder:
        component_category = ComponentCategory.SCORER

        def seed(self, input):
            raise AssertionError("not called")

    solver = build_mvp_solver(population_size=4)

    with pytest.raises(SolverConfigurationError):
        replace(
            solver,
            seeders=(SeederBinding("wrong", WrongCategorySeeder(), 4),),
        )
