"""Data models shared by all techniques and the tool layer."""

from __future__ import annotations

import operator
from enum import Enum

from pydantic import BaseModel


class Operation(str, Enum):
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"


_SYMBOLS = {Operation.ADD: "+", Operation.SUBTRACT: "−", Operation.MULTIPLY: "×"}
_FUNCS = {Operation.ADD: operator.add, Operation.SUBTRACT: operator.sub, Operation.MULTIPLY: operator.mul}


class Problem(BaseModel):
    a: int
    op: Operation
    b: int

    def exact(self) -> int:
        """Ground-truth answer, used to verify every shortcut."""
        return _FUNCS[self.op](self.a, self.b)

    def __str__(self) -> str:
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
