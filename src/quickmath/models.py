"""Data models shared by all techniques and the tool layer."""

from __future__ import annotations

import operator
from enum import Enum

from pydantic import BaseModel, model_validator


class Operation(str, Enum):
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    # Sum of the series a + (a + step) + (a + 2·step) + … + b.
    SERIES = "series"


_SYMBOLS = {Operation.ADD: "+", Operation.SUBTRACT: "−", Operation.MULTIPLY: "×"}
_FUNCS = {Operation.ADD: operator.add, Operation.SUBTRACT: operator.sub, Operation.MULTIPLY: operator.mul}


class Problem(BaseModel):
    a: int
    op: Operation
    b: int
    # Only used by SERIES: the gap between consecutive terms.
    step: int = 1

    @model_validator(mode="after")
    def _check_series(self) -> Problem:
        if self.op == Operation.SERIES:
            if self.step < 1:
                raise ValueError("A series needs a step of at least 1.")
            if self.b < self.a or (self.b - self.a) % self.step:
                raise ValueError(f"{self.b} is not reached from {self.a} in steps of {self.step}.")
        return self

    def terms(self) -> int:
        """How many terms a SERIES has."""
        return (self.b - self.a) // self.step + 1

    def exact(self) -> int:
        """Ground-truth answer, used to verify every shortcut."""
        if self.op == Operation.SERIES:
            # Pair the first and last terms, the second and second-to-last, ...
            return self.terms() * (self.a + self.b) // 2
        return _FUNCS[self.op](self.a, self.b)

    def __str__(self) -> str:
        if self.op == Operation.SERIES:
            # Write out short series in full; long ones as "1 + 2 + 3 + … + 100".
            if self.terms() <= 4:
                return " + ".join(str(t) for t in range(self.a, self.b + 1, self.step))
            first = [str(self.a + i * self.step) for i in range(3)]
            return " + ".join(first) + f" + … + {self.b}"
        return f"{self.a} {_SYMBOLS[self.op]} {self.b}"


class Step(BaseModel):
    say: str  # plain-language explanation for the learner
    expr: str  # the calculation done in this step
    result: int


class Solution(BaseModel):
    technique: str
    problem: str
    rule: str
    steps: list[Step]
    answer: int
    verified: bool
