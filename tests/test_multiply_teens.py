import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

teens = registry.get("multiply_teens")


def test_worked_example():
    sol = teens.solve(Problem(a=13, op=Operation.MULTIPLY, b=14))
    assert sol.problem == "13 × 14"
    assert [s.expr for s in sol.steps] == ["13 + 4", "17 × 10", "3 × 4", "170 + 12"]
    assert [s.result for s in sol.steps] == [17, 170, 12, 182]
    assert sol.answer == 182
    assert sol.verified


def test_units_product_carries():
    sol = teens.solve(Problem(a=19, op=Operation.MULTIPLY, b=18))
    assert [s.result for s in sol.steps] == [27, 270, 72, 342]


@given(st.integers(10, 19), st.integers(10, 19))
def test_always_matches_arithmetic(a, b):
    assert teens.solve(Problem(a=a, op=Operation.MULTIPLY, b=b)).answer == a * b


@pytest.mark.parametrize("a, b", [(9, 14), (13, 20), (13, 140), (-13, 14), (13.5, 14)])
def test_not_applicable(a, b):
    assert not teens.applies(Problem(a=a, op=Operation.MULTIPLY, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.SUBTRACT, Operation.DIVIDE])
def test_only_multiplication(op):
    assert not teens.applies(Problem(a=13, op=op, b=14))


def test_power_of_10_wins_for_10():
    names = [t.name for t in registry.find_applicable(Problem(a=10, op=Operation.MULTIPLY, b=17))]
    assert names == ["multiply_by_power_of_10", "multiply_teens"]
