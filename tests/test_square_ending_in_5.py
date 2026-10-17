import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

square = registry.get("square_ending_in_5")


def test_worked_example():
    sol = square.solve(Problem(a=35, op=Operation.MULTIPLY, b=35))
    assert sol.problem == "35 × 35"
    assert [s.say for s in sol.steps] == [
        "Take the part of 35 before the 5",
        "Multiply 3 by one more than itself, 4",
        "Put 25 after 12",
    ]
    assert [s.expr for s in sol.steps] == ["35 → 3", "3 × 4", "12 | 25"]
    assert [s.result for s in sol.steps] == [3, 12, 1225]
    assert sol.answer == 1225
    assert sol.verified


def test_three_digits():
    sol = square.solve(Problem(a=115, op=Operation.MULTIPLY, b=115))
    assert [s.expr for s in sol.steps] == ["115 → 11", "11 × 12", "132 | 25"]
    assert sol.answer == 13225


@given(st.integers(1, 10**8))
def test_always_matches_arithmetic(front):
    n = front * 10 + 5
    assert square.solve(Problem(a=n, op=Operation.MULTIPLY, b=n)).answer == n * n


@pytest.mark.parametrize("a, b", [(35, 45), (34, 34), (5, 5), (-35, -35), (0, 0), (3.5, 3.5)])
def test_not_applicable(a, b):
    assert not square.applies(Problem(a=a, op=Operation.MULTIPLY, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.SUBTRACT, Operation.DIVIDE])
def test_only_multiplication(op):
    assert not square.applies(Problem(a=35, op=op, b=35))


@pytest.mark.parametrize(
    "n, other",
    [(15, "multiply_teens"), (25, "multiply_by_25")],
)
def test_ranks_above_other_tricks(n, other):
    names = [t.name for t in registry.find_applicable(Problem(a=n, op=Operation.MULTIPLY, b=n))]
    assert names == ["square_ending_in_5", "multiply_ends_add_to_10", other]
