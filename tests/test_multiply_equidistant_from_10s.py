import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

equidistant = registry.get("multiply_equidistant_from_10s")


def test_worked_example():
    sol = equidistant.solve(Problem(a=28, op=Operation.MULTIPLY, b=32))
    assert sol.problem == "28 × 32"
    assert [s.say for s in sol.steps] == [
        "Find the central number halfway between 28 and 32",
        "Count the zeros at the end of 30",
        "Ignore the zeros and square what is left, 3",
        "Put 2 zeros after 9, double the 1 zero in 30",
        "Find how far 28 and 32 are from 30",
        "Square the distance, 2",
        "Take 4 away from 900",
    ]
    assert [s.expr for s in sol.steps] == [
        "(28 + 32) ÷ 2",
        "zeros at the end of 30",
        "3 × 3",
        "9 | 00",
        "32 − 30",
        "2 × 2",
        "900 − 4",
    ]
    assert [s.result for s in sol.steps] == [30, 1, 9, 900, 2, 4, 896]
    assert sol.answer == 896
    assert sol.verified


def test_larger_number_first():
    sol = equidistant.solve(Problem(a=203, op=Operation.MULTIPLY, b=197))
    assert sol.steps[0].expr == "(203 + 197) ÷ 2"
    assert [s.expr for s in sol.steps][4:] == ["203 − 200", "3 × 3", "40000 − 9"]
    assert sol.answer == 39991


@given(st.integers(1, 10**6), st.integers(1, 9))
def test_always_matches_arithmetic(tens, gap):
    central = tens * 10
    a, b = central - gap, central + gap
    assert equidistant.solve(Problem(a=a, op=Operation.MULTIPLY, b=b)).answer == a * b


@pytest.mark.parametrize(
    "a, b",
    [(30, 30), (24, 26), (27, 32), (20, 40), (15, 45), (-28, -32), (2.8, 3.2)],
)
def test_not_applicable(a, b):
    assert not equidistant.applies(Problem(a=a, op=Operation.MULTIPLY, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.SUBTRACT, Operation.DIVIDE])
def test_only_multiplication(op):
    assert not equidistant.applies(Problem(a=28, op=op, b=32))


@pytest.mark.parametrize(
    "a, b, other",
    [(5, 15, "multiply_by_5"), (9, 11, "multiply_by_9"), (15, 25, "multiply_by_25")],
)
def test_ranks_above_multiplying_by_one_number(a, b, other):
    names = [t.name for t in registry.find_applicable(Problem(a=a, op=Operation.MULTIPLY, b=b))]
    assert names == ["multiply_equidistant_from_10s", other]


def test_ranks_below_multiply_by_11():
    names = [t.name for t in registry.find_applicable(Problem(a=11, op=Operation.MULTIPLY, b=29))]
    assert names == ["multiply_by_11", "multiply_equidistant_from_10s"]
