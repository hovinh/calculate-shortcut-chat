import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

ends = registry.get("multiply_ends_add_to_10")


def test_worked_example():
    sol = ends.solve(Problem(a=28, op=Operation.MULTIPLY, b=22))
    assert sol.problem == "28 × 22"
    assert [s.say for s in sol.steps] == [
        "Take the part that is the same in 28 and 22",
        "Multiply 2 by one more than itself, 3",
        "Multiply the last digits, which add up to 10",
        "Put 16 after 6",
    ]
    assert [s.expr for s in sol.steps] == ["28, 22 → 2", "2 × 3", "8 × 2", "6 | 16"]
    assert [s.result for s in sol.steps] == [2, 6, 16, 616]
    assert sol.answer == 616
    assert sol.verified


def test_single_digit_product_gets_a_0():
    sol = ends.solve(Problem(a=11, op=Operation.MULTIPLY, b=19))
    assert sol.steps[-1].say == "Put 09 after 2, with a 0 in front of the 9 since it is a single digit"
    assert [s.expr for s in sol.steps] == ["11, 19 → 1", "1 × 2", "1 × 9", "2 | 09"]
    assert sol.answer == 209


def test_three_digits():
    sol = ends.solve(Problem(a=113, op=Operation.MULTIPLY, b=117))
    assert [s.expr for s in sol.steps] == ["113, 117 → 11", "11 × 12", "3 × 7", "132 | 21"]
    assert sol.answer == 13221


@given(st.integers(1, 10**8), st.integers(1, 9))
def test_always_matches_arithmetic(front, unit):
    a, b = front * 10 + unit, front * 10 + 10 - unit
    assert ends.solve(Problem(a=a, op=Operation.MULTIPLY, b=b)).answer == a * b


@pytest.mark.parametrize("a, b", [(28, 32), (28, 23), (20, 20), (4, 6), (-28, -22), (2.8, 2.2)])
def test_not_applicable(a, b):
    assert not ends.applies(Problem(a=a, op=Operation.MULTIPLY, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.SUBTRACT, Operation.DIVIDE])
def test_only_multiplication(op):
    assert not ends.applies(Problem(a=28, op=op, b=22))


def test_ranks_above_11_and_teens():
    names = [t.name for t in registry.find_applicable(Problem(a=11, op=Operation.MULTIPLY, b=19))]
    assert names == ["multiply_ends_add_to_10", "multiply_by_11", "multiply_teens"]
