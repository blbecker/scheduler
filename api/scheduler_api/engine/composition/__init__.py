"""Composition protocol extensions for operator composition patterns."""

import random
from typing import Protocol, TypeVar, Generic, Optional, Callable, Any
from copy import deepcopy
from ..interfaces import GenomeOperator

# Type variables
T = TypeVar("T")  # Context type
G = TypeVar("G")  # Genome type


class CompositionProtocol(Protocol[T, G]):
    """Protocol for operator composition patterns."""

    name: str

    def apply(self, genome: G, context: T) -> G:
        """Apply composed operation to genome."""
        ...


class ChainOperator(CompositionProtocol[T, G]):
    """Execute operators in sequence: A → B → C."""

    def __init__(self, operators: list[GenomeOperator[G, T]]):
        self.operators = operators
        self.name = f"chain_operator({len(operators)}_ops)"

    def apply(self, genome: G, context: T) -> G:
        """Apply operators sequentially."""
        current = self._copy_genome(genome)
        for op in self.operators:
            current = op.apply(current, context)
        return current

    def __str__(self) -> str:
        return f"ChainOperator[{len(self.operators)} operators]"

    def _copy_genome(self, genome: G) -> G:
        """Create a copy of the genome, handling different genome types."""
        try:
            # Try to use genome's copy method if it exists
            return genome.copy()
        except AttributeError:
            # Fallback to deepcopy
            return deepcopy(genome)


class WeightedOperator(CompositionProtocol[T, G]):
    """Apply operators with weighted probability."""

    def __init__(self, operators: list[tuple[GenomeOperator[G, T], float]]):
        # Normalize weights to sum to 1.0
        total_weight = sum(weight for _, weight in operators)
        self.operators = [(op, weight / total_weight) for op, weight in operators]
        self.name = f"weighted_operator({len(operators)}_weights)"

    def apply(self, genome: G, context: T) -> G:
        """Apply operator based on weighted random selection."""
        if not self.operators:
            return self._copy_genome(genome)

        rand = random.random()
        cumulative = 0.0
        for op, weight in self.operators:
            cumulative += weight
            if rand <= cumulative:
                return op.apply(genome, context)

        # Fallback: return original genome (should not reach here if weights sum to 1.0)
        return self._copy_genome(genome)

    def __str__(self) -> str:
        return f"WeightedOperator[{len(self.operators)} operators]"

    def _copy_genome(self, genome: G) -> G:
        """Create a copy of the genome, handling different genome types."""
        try:
            # Try to use genome's copy method if it exists
            return genome.copy()
        except AttributeError:
            # Fallback to deepcopy
            return deepcopy(genome)


class ConditionalOperator(CompositionProtocol[T, G]):
    """Apply operator based on condition."""

    def __init__(
        self,
        condition: Callable[[G, T], bool],
        operator: GenomeOperator[G, T],
        name: Optional[str] = None,
    ):
        self.condition = condition
        self.operator = operator
        self.name = name or f"conditional_operator({operator.name})"

    def apply(self, genome: G, context: T) -> G:
        """Apply operator if condition is met."""
        if self.condition(genome, context):
            return self.operator.apply(genome, context)
        return self._copy_genome(genome)

    def __str__(self) -> str:
        return f"ConditionalOperator[{self.operator.name}]"

    def _copy_genome(self, genome: G) -> G:
        """Create a copy of the genome, handling different genome types."""
        try:
            # Try to use genome's copy method if it exists
            return genome.copy()
        except AttributeError:
            # Fallback to deepcopy
            return deepcopy(genome)


class ParallelOperator(CompositionProtocol[T, G]):
    """Apply multiple operators and select best result."""

    def __init__(
        self, operators: list[GenomeOperator[G, T]], selector: Optional[Callable] = None
    ):
        self.operators = operators
        self.selector = selector or (
            lambda results: max(results, key=lambda x: x[1])[0]
        )
        self.name = f"parallel_operator({len(operators)}_ops)"

    def apply(self, genome: G, context: T) -> G:
        """Apply all operators and select best result."""
        if not self.operators:
            return self._copy_genome(genome)

        results = []
        for op in self.operators:
            result = op.apply(self._copy_genome(genome), context)
            # For now, we can't score without scorers, so we'll just pick the first
            # In practice, this would need scorers to evaluate results
            results.append(result)

        # Default: return first result
        # TODO: Integrate with scoring to select best result
        return results[0]

    def __str__(self) -> str:
        return f"ParallelOperator[{len(self.operators)} operators]"

    def _copy_genome(self, genome: G) -> G:
        """Create a copy of the genome, handling different genome types."""
        try:
            # Try to use genome's copy method if it exists
            return genome.copy()
        except AttributeError:
            # Fallback to deepcopy
            return deepcopy(genome)
