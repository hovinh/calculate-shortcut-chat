import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

nine = registry.get("multiply_by_9")


def test_worked_example():
    sol = nine.solve(Problem(a=47, op=Operation.MULTIPLY, b=9))
    assert sol.problem == "47 × 9"
    assert [s.expr for s in sol.steps] == ["47 × 10", "470 − 47"]
    assert [s.result for s in sol.steps] == [470, 423]
    assert sol.answer == 423
    assert sol.verified


def test_nine_first():
    sol = nine.solve(Problem(a=9, op=Operation.MULTIPLY, b=128))
    assert [s.expr for s in sol.steps] == ["128 × 10", "1280 − 128"]
    assert sol.answer == 1152


@given(st.integers(1, 10**9), st.booleans())
def test_always_matches_arithmetic(n, nine_first):
    a, b = (9, n) if nine_first else (n, 9)
    assert nine.solve(Problem(a=a, op=Operation.MULTIPLY, b=b)).answer == n * 9


@pytest.mark.parametrize("a, b", [(47, 8), (47, 99), (-47, 9), (0, 9), (4.7, 9)])
def test_not_applicable(a, b):
    assert not nine.applies(Problem(a=a, op=Operation.MULTIPLY, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.SUBTRACT, Operation.DIVIDE])
def test_only_multiplication(op):
    assert not nine.applies(Problem(a=47, op=op, b=9))


def test_power_of_10_wins_for_100():
    names = [t.name for t in registry.find_applicable(Problem(a=9, op=Operation.MULTIPLY, b=100))]
    assert names == ["multiply_by_power_of_10", "multiply_by_9"]
