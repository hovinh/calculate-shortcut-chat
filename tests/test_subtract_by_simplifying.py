import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

simp = registry.get("subtract_by_simplifying")


def test_worked_example():
    sol = simp.solve(Problem(a=1103, op=Operation.SUBTRACT, b=38))
    assert sol.problem == "1103 − 38"
    assert [s.say for s in sol.steps] == [
        "Take 3 away from both numbers, so 1103 − 38 becomes 1100 − 35",
        "Take 5 away from both numbers, so 1100 − 35 becomes 1095 − 30",
        "Now take away the round number",
    ]
    assert [s.expr for s in sol.steps] == ["1103 − 3", "1100 − 5", "1095 − 30"]
    assert [s.result for s in sol.steps] == [1100, 1095, 1065]
    assert sol.answer == 1065
    assert sol.verified


def test_already_round_skips_first_step():
    sol = simp.solve(Problem(a=1100, op=Operation.SUBTRACT, b=35))
    assert [s.expr for s in sol.steps] == ["1100 − 5", "1095 − 30"]
    assert sol.answer == 1065


@given(st.integers(10, 10**9), st.integers(10, 10**9))
def test_always_matches_arithmetic(a, b):
    a, b = max(a, b), min(a, b)
    assume(simp.applies(Problem(a=a, op=Operation.SUBTRACT, b=b)))
    assert simp.solve(Problem(a=a, op=Operation.SUBTRACT, b=b)).answer == a - b


@pytest.mark.parametrize(
    "a, b",
    [
        (1108, 35),  # no borrowing: 8 − 5 is easy already
        (1105, 35),
        (1103, 8),  # nothing left to take away at the end
        (38, 1103),
        (-1103, 38),
        (110.3, 3.8),
    ],
)
def test_not_applicable(a, b):
    assert not simp.applies(Problem(a=a, op=Operation.SUBTRACT, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.MULTIPLY, Operation.DIVIDE])
def test_only_subtraction(op):
    assert not simp.applies(Problem(a=1103, op=op, b=38))


def test_ranking():
    ranked = [t.name for t in registry.find_applicable(Problem(a=1103, op=Operation.SUBTRACT, b=38))]
    assert ranked == ["subtract_by_simplifying", "subtract_in_steps"]
    ranked = [t.name for t in registry.find_applicable(Problem(a=176, op=Operation.SUBTRACT, b=98))]
    assert ranked == ["subtract_round_and_compensate", "subtract_by_simplifying", "subtract_in_steps"]
