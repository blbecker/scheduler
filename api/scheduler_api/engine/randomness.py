from __future__ import annotations

import hashlib
import random
from uuid import UUID

from scheduler_api.engine.models.phase import PhaseType


def derive_seed(
    base_seed: int,
    generation: int,
    phase: PhaseType,
    component_id: str,
    component_index: int,
) -> int:
    """Derive a stable, non-negative seed from algorithm context."""

    material = (
        f"{base_seed}:{generation}:{phase.value}:" f"{component_id}:{component_index}"
    )
    digest = hashlib.sha256(material.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % (2**63)


def uuid_from_rng(rng: random.Random) -> UUID:
    """Create a deterministic UUID from an explicit random generator."""

    return UUID(int=rng.getrandbits(128), version=4)
