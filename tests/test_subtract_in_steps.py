import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

sub = registry.get("subtract_in_steps")


def test_worked_example():
    sol = sub.solve(Problem(a=83, op=Operation.SUBTRACT, b=27))
    assert sol.problem == "83 − 27"
    assert sol.steps[0].say == "Split 27 into 20 + 7, then take away 20 first"
    assert [s.expr for s in sol.steps] == ["83 − 20", "63 − 7"]
    assert [s.result for s in sol.steps] == [63, 56]
    assert sol.answer == 56
    assert sol.verified


def test_three_parts():
    sol = sub.solve(Problem(a=567, op=Operation.SUBTRACT, b=234))
    assert [s.expr for s in sol.steps] == ["567 − 200", "367 − 30", "337 − 4"]
    assert sol.answer == 333


def test_skips_zero_parts():
    sol = sub.solve(Problem(a=5000, op=Operation.SUBTRACT, b=1205))
    assert sol.steps[0].say == "Split 1205 into 1000 + 200 + 5, then take away 1000 first"
    assert [s.result for s in sol.steps] == [4000, 3800, 3795]


@given(st.integers(1, 10**9), st.integers(1, 10**9))
def test_always_matches_arithmetic(a, b):
    a, b = max(a, b), min(a, b)
    assume(sub.applies(Problem(a=a, op=Operation.SUBTRACT, b=b)))
    assert sub.solve(Problem(a=a, op=Operation.SUBTRACT, b=b)).answer == a - b


@pytest.mark.parametrize(
    "a, b",
    [
        (83, 7),  # only one part
        (83, 20),
        (27, 83),  # would go below zero
        (-83, 27),
        (83, -27),
        (8.3, 2.7),
    ],
)
def test_not_applicable(a, b):
    assert not sub.applies(Problem(a=a, op=Operation.SUBTRACT, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.MULTIPLY, Operation.DIVIDE])
def test_only_subtraction(op):
    assert not sub.applies(Problem(a=83, op=op, b=27))


def test_ranks_last():
    ranked = registry.find_applicable(Problem(a=176, op=Operation.SUBTRACT, b=98))
    assert [t.name for t in ranked][-1] == "subtract_in_steps"
