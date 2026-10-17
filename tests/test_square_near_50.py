import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

near_50 = registry.get("square_near_50")


def test_worked_example_below_50():
    sol = near_50.solve(Problem(a=47, op=Operation.MULTIPLY, b=47))
    assert sol.problem == "47 × 47"
    assert [s.say for s in sol.steps] == [
        "Subtract 50 from 47",
        "Add -3 to 25",
        "Square the difference of 47 from 50, 3",
        "Put 09 after 22, with a 0 in front of the 9 since it is a single digit",
    ]
    assert [s.expr for s in sol.steps] == ["47 − 50", "25 − 3", "3 × 3", "22 | 09"]
    assert [s.result for s in sol.steps] == [-3, 22, 9, 2209]
    assert sol.answer == 2209
    assert sol.verified


def test_above_50_two_digit_square():
    sol = near_50.solve(Problem(a=56, op=Operation.MULTIPLY, b=56))
    assert [s.expr for s in sol.steps] == ["56 − 50", "25 + 6", "6 × 6", "31 | 36"]
    assert sol.steps[-1].say == "Put 36 after 31"
    assert sol.answer == 3136


def test_three_digit_square_carries():
    sol = near_50.solve(Problem(a=62, op=Operation.MULTIPLY, b=62))
    assert [s.say for s in sol.steps][3:] == [
        "Keep the right two digits of 144, 44, and carry 1 over to 37",
        "Put 44 after 38",
    ]
    assert [s.expr for s in sol.steps] == ["62 − 50", "25 + 12", "12 × 12", "37 + 1", "38 | 44"]
    assert sol.answer == 3844


def test_three_digit_square_with_0_in_the_tens():
    sol = near_50.solve(Problem(a=40, op=Operation.MULTIPLY, b=40))
    assert [s.expr for s in sol.steps] == ["40 − 50", "25 − 10", "10 × 10", "15 + 1", "16 | 00"]
    assert sol.answer == 1600


@given(st.integers(35, 65))
def test_always_matches_arithmetic(n):
    assert near_50.solve(Problem(a=n, op=Operation.MULTIPLY, b=n)).answer == n * n


@pytest.mark.parametrize("a, b", [(47, 48), (34, 34), (66, 66), (-47, -47), (4.7, 4.7)])
def test_not_applicable(a, b):
    assert not near_50.applies(Problem(a=a, op=Operation.MULTIPLY, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.SUBTRACT, Operation.DIVIDE])
def test_only_multiplication(op):
    assert not near_50.applies(Problem(a=47, op=op, b=47))


def test_ranks_below_ending_in_5_tricks():
    names = [t.name for t in registry.find_applicable(Problem(a=45, op=Operation.MULTIPLY, b=45))]
    assert names == ["square_ending_in_5", "multiply_ends_add_to_10", "square_near_50"]
