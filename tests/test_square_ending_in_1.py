import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

square = registry.get("square_ending_in_1")


def test_worked_example():
    sol = square.solve(Problem(a=41, op=Operation.MULTIPLY, b=41))
    assert sol.problem == "41 × 41"
    assert [s.say for s in sol.steps] == [
        "Take the number 1 less than 41",
        "Count the zeros at the end of 40",
        "Ignore the zeros and square what is left, 4",
        "Put 2 zeros after 16, double the 1 zero in 40",
        "Add 41 and 40 to 1600",
    ]
    assert [s.expr for s in sol.steps] == ["41 − 1", "zeros at the end of 40", "4 × 4", "16 | 00", "1600 + 41 + 40"]
    assert [s.result for s in sol.steps] == [40, 1, 16, 1600, 1681]
    assert sol.answer == 1681
    assert sol.verified


def test_more_zeros_below():
    sol = square.solve(Problem(a=101, op=Operation.MULTIPLY, b=101))
    assert [s.expr for s in sol.steps] == ["101 − 1", "zeros at the end of 100", "1 × 1", "1 | 0000", "10000 + 101 + 100"]
    assert sol.answer == 10201


@given(st.integers(1, 10**8))
def test_always_matches_arithmetic(front):
    n = front * 10 + 1
    assert square.solve(Problem(a=n, op=Operation.MULTIPLY, b=n)).answer == n * n


@pytest.mark.parametrize("a, b", [(41, 31), (40, 40), (1, 1), (-41, -41), (4.1, 4.1)])
def test_not_applicable(a, b):
    assert not square.applies(Problem(a=a, op=Operation.MULTIPLY, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.SUBTRACT, Operation.DIVIDE])
def test_only_multiplication(op):
    assert not square.applies(Problem(a=41, op=op, b=41))


@pytest.mark.parametrize(
    "n, others",
    [(11, ["multiply_by_11", "multiply_teens"]), (41, ["square_near_50"]), (61, ["square_near_50"])],
)
def test_ranks_above_other_tricks(n, others):
    names = [t.name for t in registry.find_applicable(Problem(a=n, op=Operation.MULTIPLY, b=n))]
    assert names == ["square_ending_in_1", *others]
