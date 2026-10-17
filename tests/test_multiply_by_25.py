import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

twenty_five = registry.get("multiply_by_25")


def test_worked_example():
    sol = twenty_five.solve(Problem(a=48, op=Operation.MULTIPLY, b=25))
    assert sol.problem == "48 × 25"
    assert [s.expr for s in sol.steps] == ["48 × 100", "4800 ÷ 4"]
    assert [s.result for s in sol.steps] == [4800, 1200]
    assert sol.answer == 1200
    assert sol.verified


def test_not_a_multiple_of_4():
    sol = twenty_five.solve(Problem(a=25, op=Operation.MULTIPLY, b=37))
    assert [s.expr for s in sol.steps] == ["37 × 100", "3700 ÷ 4"]
    assert sol.answer == 925


@given(st.integers(1, 10**9), st.booleans())
def test_always_matches_arithmetic(n, twenty_five_first):
    a, b = (25, n) if twenty_five_first else (n, 25)
    assert twenty_five.solve(Problem(a=a, op=Operation.MULTIPLY, b=b)).answer == n * 25


@pytest.mark.parametrize("a, b", [(48, 24), (48, 250), (-48, 25), (0, 25), (4.8, 25)])
def test_not_applicable(a, b):
    assert not twenty_five.applies(Problem(a=a, op=Operation.MULTIPLY, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.SUBTRACT, Operation.DIVIDE])
def test_only_multiplication(op):
    assert not twenty_five.applies(Problem(a=48, op=op, b=25))


def test_power_of_10_wins_for_100():
    names = [t.name for t in registry.find_applicable(Problem(a=25, op=Operation.MULTIPLY, b=100))]
    assert names == ["multiply_by_power_of_10", "multiply_by_25"]
