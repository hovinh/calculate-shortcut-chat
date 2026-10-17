import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

square = registry.get("square_ending_in_0")


def test_worked_example():
    sol = square.solve(Problem(a=300, op=Operation.MULTIPLY, b=300))
    assert sol.problem == "300 × 300"
    assert [s.say for s in sol.steps] == [
        "Count the zeros at the end of 300",
        "Ignore the zeros and square what is left, 3",
        "Put 4 zeros after 9, double the 2 zeros in 300",
    ]
    assert [s.expr for s in sol.steps] == ["zeros at the end of 300", "3 × 3", "9 | 0000"]
    assert [s.result for s in sol.steps] == [2, 9, 90000]
    assert sol.answer == 90000
    assert sol.verified


def test_one_zero():
    sol = square.solve(Problem(a=120, op=Operation.MULTIPLY, b=120))
    assert sol.steps[-1].say == "Put 2 zeros after 144, double the 1 zero in 120"
    assert [s.expr for s in sol.steps] == ["zeros at the end of 120", "12 × 12", "144 | 00"]
    assert sol.answer == 14400


def test_only_zeros_at_the_end_count():
    sol = square.solve(Problem(a=1020, op=Operation.MULTIPLY, b=1020))
    assert [s.expr for s in sol.steps] == ["zeros at the end of 1020", "102 × 102", "10404 | 00"]
    assert sol.answer == 1040400


@given(st.integers(1, 10**6), st.integers(1, 6))
def test_always_matches_arithmetic(front, zeros):
    n = front * 10**zeros
    assert square.solve(Problem(a=n, op=Operation.MULTIPLY, b=n)).answer == n * n


@pytest.mark.parametrize("a, b", [(30, 40), (35, 35), (0, 0), (-30, -30), (3.0, 3.0)])
def test_not_applicable(a, b):
    assert not square.applies(Problem(a=a, op=Operation.MULTIPLY, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.SUBTRACT, Operation.DIVIDE])
def test_only_multiplication(op):
    assert not square.applies(Problem(a=300, op=op, b=300))


@pytest.mark.parametrize("n", [40, 50, 60])
def test_ranks_above_square_near_50(n):
    names = [t.name for t in registry.find_applicable(Problem(a=n, op=Operation.MULTIPLY, b=n))]
    assert names == ["square_ending_in_0", "square_near_50"]


@pytest.mark.parametrize("n", [10, 100])
def test_ranks_below_multiply_by_power_of_10(n):
    names = [t.name for t in registry.find_applicable(Problem(a=n, op=Operation.MULTIPLY, b=n))]
    assert names[:2] == ["multiply_by_power_of_10", "square_ending_in_0"]
