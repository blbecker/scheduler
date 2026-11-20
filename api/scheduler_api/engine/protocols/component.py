from typing import ClassVar, Protocol

from scheduler_api.engine.models.phase import ComponentCategory


class Component(Protocol):
    component_category: ClassVar[ComponentCategory]
