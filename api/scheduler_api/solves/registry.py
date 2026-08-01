"""Per-solve component registry for instantiation from DTOs."""

from typing import Any, Type, Optional
from scheduler_api.dto.solve_components import (
    ScorerDTO,
    MutatorDTO,
    ConstraintDTO,
    SelectorDTO,
    SeederDTO,
    StopConditionDTO,
)
from ..engine.interfaces import (
    Scorable,
    GenomeOperator,
    Constraint,
    Selector,
    Seeder,
    Stoppable,
)


class ComponentRegistry:
    """Registry for components specific to a solve instance.

    Components are registered at solver creation and instantiated
    lazily when needed in tasks.
    """

    def __init__(self):
        self._scorers: dict[str, Type[Scorable]] = {}
        self._mutators: dict[str, Type[GenomeOperator]] = {}
        self._constraints: dict[str, Type[Constraint]] = {}
        self._selectors: dict[str, Type[Selector]] = {}
        self._seeders: dict[str, Type[Seeder]] = {}
        self._stop_conditions: dict[str, Type[Stoppable]] = {}

    def register_scorer(self, name: str, component_class: Type[Scorable]) -> None:
        """Register a scorer class by name."""
        self._scorers[name] = component_class

    def register_mutator(
        self, name: str, component_class: Type[GenomeOperator]
    ) -> None:
        """Register a mutator class by name."""
        self._mutators[name] = component_class

    def register_constraint(self, name: str, component_class: Type[Constraint]) -> None:
        """Register a constraint class by name."""
        self._constraints[name] = component_class

    def register_selector(self, name: str, component_class: Type[Selector]) -> None:
        """Register a selector class by name."""
        self._selectors[name] = component_class

    def register_seeder(self, name: str, component_class: Type[Seeder]) -> None:
        """Register a seeder class by name."""
        self._seeders[name] = component_class

    def register_stop_condition(
        self, name: str, component_class: Type[Stoppable]
    ) -> None:
        """Register a stop condition class by name."""
        self._stop_conditions[name] = component_class

    def create_scorer(self, dto: ScorerDTO) -> Scorable:
        """Create scorer instance from DTO (lazy validation)."""
        if dto.component_type.value not in self._scorers:
            raise ValueError(f"Unknown scorer type: {dto.component_type}")

        component_class = self._scorers[dto.component_type.value]
        # Pass config as kwargs to dataclass constructor
        return component_class(**dto.config)

    def create_mutator(self, dto: MutatorDTO) -> GenomeOperator:
        """Create mutator instance from DTO (lazy validation)."""
        if dto.component_type.value not in self._mutators:
            raise ValueError(f"Unknown mutator type: {dto.component_type}")

        component_class = self._mutators[dto.component_type.value]
        return component_class(**dto.config)

    def create_constraint(self, dto: ConstraintDTO) -> Constraint:
        """Create constraint instance from DTO (lazy validation)."""
        if dto.component_type.value not in self._constraints:
            raise ValueError(f"Unknown constraint type: {dto.component_type}")

        component_class = self._constraints[dto.component_type.value]
        return component_class(**dto.config)

    def create_selector(self, dto: SelectorDTO) -> Selector:
        """Create selector instance from DTO (lazy validation)."""
        if dto.component_type.value not in self._selectors:
            raise ValueError(f"Unknown selector type: {dto.component_type}")

        component_class = self._selectors[dto.component_type.value]
        return component_class(**dto.config)

    def create_seeder(self, dto: SeederDTO) -> Seeder:
        """Create seeder instance from DTO (lazy validation)."""
        if dto.component_type.value not in self._seeders:
            raise ValueError(f"Unknown seeder type: {dto.component_type}")

        component_class = self._seeders[dto.component_type.value]
        return component_class(**dto.config)

    def create_stop_condition(self, dto: StopConditionDTO) -> Stoppable:
        """Create stop condition instance from DTO (lazy validation)."""
        if dto.component_type.value not in self._stop_conditions:
            raise ValueError(f"Unknown stop condition type: {dto.component_type}")

        component_class = self._stop_conditions[dto.component_type.value]
        return component_class(**dto.config)

    def to_dict(self) -> dict[str, Any]:
        """Convert registry to dictionary for serialization."""
        return {
            "scorers": list(self._scorers.keys()),
            "mutators": list(self._mutators.keys()),
            "constraints": list(self._constraints.keys()),
            "selectors": list(self._selectors.keys()),
            "seeders": list(self._seeders.keys()),
            "stop_conditions": list(self._stop_conditions.keys()),
        }
