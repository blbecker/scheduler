"""Base component contract.

Implementations declare ``component_id`` as a class attribute and satisfy the
category protocol structurally. No inheritance is required.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Component(Protocol):
    """Anything the registry can hold."""

    #: Stable identifier. Must match the id the component is registered under.
    component_id: str


#: Type erasure for registry storage. The registry is heterogeneous by design: it
#: holds one instance per component id across every category, and the runner
#: narrows to the concrete protocol before calling.
AnyComponent = Any
