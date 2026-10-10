from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from quickmath.models import Operation, Problem, Solution, Step


class Technique(ABC):
    """A mental-math shortcut.

    Subclasses declare metadata and implement `applies` and `steps`;
    `solve` checks the result against plain arithmetic before returning it.
    """

    name: ClassVar[str]  # tool-friendly id, e.g. "add_9"
    title: ClassVar[str]  # human-friendly, e.g. "Adding 9"
    rule: ClassVar[str]  # the idea in one or two sentences
    operation: ClassVar[Operation]
    # Higher wins when several techniques apply. Narrow, special-case tricks
    # should rank above general ones (e.g. "add 9" above "round and compensate").
    priority: ClassVar[int] = 0

    def applies(self, problem: Problem) -> bool:
        return problem.op == self.operation and self._applies(problem)

    @abstractmethod
    def _applies(self, problem: Problem) -> bool: ...

    @abstractmethod
    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        """Return the worked steps and the final answer."""

    def solve(self, problem: Problem) -> Solution:
        if not self.applies(problem):
            raise ValueError(f"{self.name} does not apply to {problem}")
        steps, answer = self.steps(problem)
        if answer != problem.exact():
            raise RuntimeError(f"{self.name} produced {answer} for {problem}, expected {problem.exact()}")
        return Solution(
            technique=self.name,
            problem=str(problem),
            rule=self.rule,
            steps=steps,
            answer=answer,
            verified=True,
        )
