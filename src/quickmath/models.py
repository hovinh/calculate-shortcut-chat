"""Data models shared by all techniques and the tool layer."""

from __future__ import annotations

import operator
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, PlainSerializer, WithJsonSchema, model_validator


def number(x: Any) -> Any:
    """Whole numbers become int; other numbers an exact Decimal (4.7 stays 4.7, not 4.700000000000001).

    Anything that isn't a number is passed through for pydantic to reject.
    """
    if isinstance(x, float):
        x = Decimal(repr(x))
    elif isinstance(x, str):
        try:
            x = Decimal(x.strip())
        except InvalidOperation:
            return x
    if isinstance(x, Decimal) and x.is_finite():
        return int(x) if x == x.to_integral_value() else x.normalize()
    return x


def json_number(x: int | Decimal) -> int | float:
    return x if isinstance(x, int) else float(x)


def fmt(x: int | Decimal) -> str:
    """Plain notation, never scientific: 0.0000001, not 1E-7."""
    return str(x) if isinstance(x, int) else format(x, "f")


# A whole number or a decimal. Sent to the LLM (and logged) as a plain JSON number.
Number = Annotated[
    int | Decimal,
    BeforeValidator(number),
    PlainSerializer(json_number, when_used="json"),
    WithJsonSchema({"type": "number"}),
]


class Operation(str, Enum):
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    # Sum of the series a + (a + step) + (a + 2·step) + … + b.
    SERIES = "series"


_SYMBOLS = {Operation.ADD: "+", Operation.SUBTRACT: "−", Operation.MULTIPLY: "×"}
_FUNCS = {Operation.ADD: operator.add, Operation.SUBTRACT: operator.sub, Operation.MULTIPLY: operator.mul}


class Problem(BaseModel):
    a: Number
    op: Operation
    b: Number
    # Only used by SERIES: the gap between consecutive terms.
    step: int = 1

    @model_validator(mode="after")
    def _check_series(self) -> Problem:
        if self.op == Operation.SERIES:
            if not self.is_whole():
                raise ValueError("A series needs whole-number terms.")
            if self.step < 1:
                raise ValueError("A series needs a step of at least 1.")
            if self.b < self.a or (self.b - self.a) % self.step:
                raise ValueError(f"{self.b} is not reached from {self.a} in steps of {self.step}.")
        return self

    def is_whole(self) -> bool:
        """True when neither operand is a decimal."""
        return isinstance(self.a, int) and isinstance(self.b, int)

    def terms(self) -> int:
        """How many terms a SERIES has."""
        return (self.b - self.a) // self.step + 1

    def exact(self) -> int | Decimal:
        """Ground-truth answer, used to verify every shortcut."""
        if self.op == Operation.SERIES:
            # Pair the first and last terms, the second and second-to-last, ...
            return self.terms() * (self.a + self.b) // 2
        return number(_FUNCS[self.op](self.a, self.b))

    def __str__(self) -> str:
        if self.op == Operation.SERIES:
            # Write out short series in full; long ones as "1 + 2 + 3 + … + 100".
            if self.terms() <= 4:
                return " + ".join(str(t) for t in range(self.a, self.b + 1, self.step))
            first = [str(self.a + i * self.step) for i in range(3)]
            return " + ".join(first) + f" + … + {self.b}"
        return f"{fmt(self.a)} {_SYMBOLS[self.op]} {fmt(self.b)}"


class Step(BaseModel):
    say: str  # plain-language explanation for the learner
    expr: str  # the calculation done in this step
    result: Number


class Solution(BaseModel):
    technique: str
    problem: str
    rule: str
    steps: list[Step]
    answer: Number
    verified: bool
