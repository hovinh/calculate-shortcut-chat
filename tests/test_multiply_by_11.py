import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

eleven = registry.get("multiply_by_11")


def test_worked_example():
    sol = eleven.solve(Problem(a=2341, op=Operation.MULTIPLY, b=11))
    assert sol.problem == "2341 × 11"
    assert [s.say for s in sol.steps] == [
        "Write down the rightmost digit of 2341, 1, as it is",
        "Add 4 to the digit on its right, 1, write 5",
        "Add 3 to the digit on its right, 4, write 7",
        "Add 2 to the digit on its right, 3, write 5",
        "Write the leftmost digit, 2",
        "Read the answer line from left to right",
    ]
    assert [s.expr for s in sol.steps] == ["1", "4 + 1", "3 + 4", "2 + 3", "2", "2 | 5 | 7 | 5 | 1"]
    assert sol.answer == 25751
    assert sol.verified


def test_carrying():
    sol = eleven.solve(Problem(a=11, op=Operation.MULTIPLY, b=87))
    assert [s.say for s in sol.steps] == [
        "Write down the rightmost digit of 87, 7, as it is",
        "Add 8 to the digit on its right, 7, write 5 and carry 1",
        "Write the leftmost digit, 8, plus the 1 carried",
        "Read the answer line from left to right",
    ]
    assert [s.expr for s in sol.steps] == ["7", "8 + 7", "8 + 1", "9 | 5 | 7"]
    assert sol.answer == 957


def test_carry_into_next_pair_and_past_leftmost():
    sol = eleven.solve(Problem(a=995, op=Operation.MULTIPLY, b=11))
    assert [s.expr for s in sol.steps] == ["5", "9 + 5", "9 + 9 + 1", "9 + 1", "10 | 9 | 4 | 5"]
    assert sol.answer == 10945


@given(st.integers(10, 10**12), st.booleans())
def test_always_matches_arithmetic(n, eleven_first):
    a, b = (11, n) if eleven_first else (n, 11)
    assert eleven.solve(Problem(a=a, op=Operation.MULTIPLY, b=b)).answer == n * 11


@pytest.mark.parametrize("a, b", [(47, 12), (7, 11), (11, 9), (-47, 11), (0, 11), (4.7, 11)])
def test_not_applicable(a, b):
    assert not eleven.applies(Problem(a=a, op=Operation.MULTIPLY, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.SUBTRACT, Operation.DIVIDE])
def test_only_multiplication(op):
    assert not eleven.applies(Problem(a=47, op=op, b=11))


def test_ranks_above_teens():
    names = [t.name for t in registry.find_applicable(Problem(a=11, op=Operation.MULTIPLY, b=13))]
    assert names == ["multiply_by_11", "multiply_teens"]
