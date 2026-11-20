from typing import Protocol

from scheduler_api.engine.models.phase import (
    ComponentInvocation,
    ComponentResult,
)


class Runner(Protocol):
    def run(self, invocation: ComponentInvocation) -> ComponentResult: ...
