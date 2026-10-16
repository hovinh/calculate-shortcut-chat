import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

groups = registry.get("subtract_in_groups")


def test_worked_example():
    sol = groups.solve(Problem(a=6218, op=Operation.SUBTRACT, b=4753))
    assert sol.problem == "6218 − 4753"
    assert [s.say for s in sol.steps] == [
        "Split into groups of two digits: 62 | 18 and 47 | 53. Subtract the groups: 62 − 47",
        "18 is smaller than 53, so subtract the other way round and take this away at the end",
        "Put the groups back in their places and add or take away",
    ]
    assert [s.expr for s in sol.steps] == ["62 − 47", "53 − 18", "1500 − 35"]
    assert [s.result for s in sol.steps] == [15, 35, 1465]
    assert sol.answer == 1465
    assert sol.verified


def test_no_adjusting_needed():
    sol = groups.solve(Problem(a=6253, op=Operation.SUBTRACT, b=4718))
    assert [s.expr for s in sol.steps] == ["62 − 47", "53 − 18", "1500 + 35"]
    assert sol.answer == 1535


def test_three_groups():
    sol = groups.solve(Problem(a=351862, op=Operation.SUBTRACT, b=128947))
    assert [s.expr for s in sol.steps] == ["35 − 12", "89 − 18", "62 − 47", "230000 − 7100 + 15"]
    assert sol.answer == 222915


def test_odd_digit_count():
    sol = groups.solve(Problem(a=532, op=Operation.SUBTRACT, b=278))
    assert [s.expr for s in sol.steps] == ["5 − 2", "78 − 32", "300 − 46"]
    assert sol.answer == 254


@given(st.integers(100, 10**12), st.integers(100, 10**12))
def test_always_matches_arithmetic(a, b):
    a, b = max(a, b), min(a, b)
    assume(groups.applies(Problem(a=a, op=Operation.SUBTRACT, b=b)))
    assert groups.solve(Problem(a=a, op=Operation.SUBTRACT, b=b)).answer == a - b


@pytest.mark.parametrize("a, b", [(1103, 38), (4753, 6218), (-6218, 4753), (621.8, 475.3)])
def test_not_applicable(a, b):
    assert not groups.applies(Problem(a=a, op=Operation.SUBTRACT, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.MULTIPLY, Operation.DIVIDE])
def test_only_subtraction(op):
    assert not groups.applies(Problem(a=6218, op=op, b=4753))


def test_ranking():
    ranked = [t.name for t in registry.find_applicable(Problem(a=6218, op=Operation.SUBTRACT, b=4753))]
    assert ranked == ["subtract_in_groups", "subtract_in_steps"]
    ranked = [t.name for t in registry.find_applicable(Problem(a=1176, op=Operation.SUBTRACT, b=198))]
    assert ranked[0] == "subtract_round_and_compensate"


def test_equal_front_groups():
    sol = groups.solve(Problem(a=6253, op=Operation.SUBTRACT, b=6218))
    assert [s.expr for s in sol.steps] == ["62 − 62", "53 − 18", "35"]
    assert sol.answer == 35
