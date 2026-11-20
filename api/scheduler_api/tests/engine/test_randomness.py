from __future__ import annotations

import random

from scheduler_api.engine.models.phase import PhaseType
from scheduler_api.engine.randomness import derive_seed, uuid_from_rng


def test_derive_seed_is_deterministic():
    first = derive_seed(7, 0, PhaseType.SEED, "random_schedule", 0)
    second = derive_seed(7, 0, PhaseType.SEED, "random_schedule", 0)

    assert first == second
    assert first >= 0


def test_derive_seed_varies_with_context():
    base = derive_seed(7, 0, PhaseType.SEED, "random_schedule", 0)
    assert base != derive_seed(8, 0, PhaseType.SEED, "random_schedule", 0)
    assert base != derive_seed(7, 1, PhaseType.SEED, "random_schedule", 0)
    assert base != derive_seed(7, 0, PhaseType.MUTATE, "random_schedule", 0)
    assert base != derive_seed(7, 0, PhaseType.SEED, "other", 0)
    assert base != derive_seed(7, 0, PhaseType.SEED, "random_schedule", 1)


def test_uuid_from_rng_is_deterministic():
    first = uuid_from_rng(random.Random(123))
    second = uuid_from_rng(random.Random(123))
    third = uuid_from_rng(random.Random(124))

    assert first == second
    assert first != third
    assert first.version == 4
