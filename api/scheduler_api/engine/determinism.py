"""Deterministic seed and identifier derivation.

An execution must be reproducible: the same problem, request, and seed must
produce an identical result. That rules out module-global random state and
runtime-generated UUIDs, so every seed and id the engine creates is derived from
stable coordinates here.
"""

from __future__ import annotations

import hashlib
from uuid import UUID, uuid5

#: Fixed namespace for every id the engine derives.
ENGINE_NAMESPACE = uuid5(
    UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8"), "scheduler-engine"
)


def derive_uuid(*parts: object) -> UUID:
    """Derive a stable UUID from an ordered tuple of coordinates."""
    joined = ":".join(str(part) for part in parts)
    return uuid5(ENGINE_NAMESPACE, joined)


def derive_seed(master_seed: int, *parts: object) -> int:
    """Derive a component seed from the master seed plus stable coordinates."""
    joined = ":".join([str(master_seed), *(str(part) for part in parts)])
    digest = hashlib.blake2b(joined.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big")
