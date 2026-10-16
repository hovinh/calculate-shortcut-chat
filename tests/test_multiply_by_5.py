import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

five = registry.get("multiply_by_5")


def test_worked_example():
    sol = five.solve(Problem(a=48, op=Operation.MULTIPLY, b=5))
    assert sol.problem == "48 × 5"
    assert [s.expr for s in sol.steps] == ["48 × 10", "480 ÷ 2"]
    assert [s.result for s in sol.steps] == [480, 240]
    assert sol.answer == 240
    assert sol.verified


def test_odd_number():
    sol = five.solve(Problem(a=5, op=Operation.MULTIPLY, b=47))
    assert [s.expr for s in sol.steps] == ["47 × 10", "470 ÷ 2"]
    assert sol.answer == 235


@given(st.integers(1, 10**9), st.booleans())
def test_always_matches_arithmetic(n, five_first):
    a, b = (5, n) if five_first else (n, 5)
    assert five.solve(Problem(a=a, op=Operation.MULTIPLY, b=b)).answer == n * 5


@pytest.mark.parametrize("a, b", [(48, 6), (48, 50), (-48, 5), (0, 5), (4.8, 5)])
def test_not_applicable(a, b):
    assert not five.applies(Problem(a=a, op=Operation.MULTIPLY, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.SUBTRACT, Operation.DIVIDE])
def test_only_multiplication(op):
    assert not five.applies(Problem(a=48, op=op, b=5))


def test_power_of_10_wins_for_100():
    names = [t.name for t in registry.find_applicable(Problem(a=5, op=Operation.MULTIPLY, b=100))]
    assert names == ["multiply_by_power_of_10", "multiply_by_5"]
