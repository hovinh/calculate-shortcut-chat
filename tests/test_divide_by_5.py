from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

five = registry.get("divide_by_5")


def test_worked_example():
    sol = five.solve(Problem(a=47, op=Operation.DIVIDE, b=5))
    assert sol.problem == "47 ÷ 5"
    assert [s.expr for s in sol.steps] == ["47 × 2", "94 ÷ 10"]
    assert [s.result for s in sol.steps] == [94, Decimal("9.4")]
    assert sol.answer == Decimal("9.4")
    assert sol.verified


def test_whole_answer():
    sol = five.solve(Problem(a=45, op=Operation.DIVIDE, b=5))
    assert [s.expr for s in sol.steps] == ["45 × 2", "90 ÷ 10"]
    assert sol.answer == 9


def test_decimal():
    sol = five.solve(Problem(a=4.7, op=Operation.DIVIDE, b=5))
    assert [s.expr for s in sol.steps] == ["4.7 × 2", "9.4 ÷ 10"]
    assert sol.answer == Decimal("0.94")


@given(st.integers(1, 10**9))
def test_always_matches_arithmetic(n):
    assert five.solve(Problem(a=n, op=Operation.DIVIDE, b=5)).answer == Decimal(n) / 5


@given(st.decimals(min_value="0.001", max_value="100000", places=3))
def test_decimals_match_arithmetic(n):
    assert five.solve(Problem(a=n, op=Operation.DIVIDE, b=5)).answer == n / 5


@pytest.mark.parametrize("a, b", [(47, 6), (47, 50), (-47, 5), (0, 5), (5, 47)])
def test_not_applicable(a, b):
    assert not five.applies(Problem(a=a, op=Operation.DIVIDE, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.SUBTRACT, Operation.MULTIPLY])
def test_only_division(op):
    assert not five.applies(Problem(a=47, op=op, b=5))
