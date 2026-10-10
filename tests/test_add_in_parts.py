import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

parts = registry.get("add_in_parts")

# At least 10 and not ending in 0.
splittable = st.integers(10, 10**9).filter(lambda x: x % 10 != 0)


def test_worked_example():
    sol = parts.solve(Problem(a=123, op=Operation.ADD, b=46))
    assert [s.expr for s in sol.steps] == ["120 + 40", "3 + 6", "160 + 9"]
    assert [s.result for s in sol.steps] == [160, 9, 169]
    assert sol.answer == 169
    assert sol.verified


def test_ones_that_carry():
    sol = parts.solve(Problem(a=127, op=Operation.ADD, b=46))
    assert [s.result for s in sol.steps] == [160, 13, 173]


@given(splittable, splittable)
def test_always_matches_arithmetic(a, b):
    assert parts.solve(Problem(a=a, op=Operation.ADD, b=b)).answer == a + b


@pytest.mark.parametrize(
    "a, b",
    [
        (123, 6),  # single digit has no tens part
        (120, 46),  # ends in 0, no ones part
        (123, 40),
        (-23, 46),
    ],
)
def test_not_applicable(a, b):
    assert not parts.applies(Problem(a=a, op=Operation.ADD, b=b))


@pytest.mark.parametrize("op", [Operation.SUBTRACT, Operation.MULTIPLY])
def test_only_addition(op):
    assert not parts.applies(Problem(a=123, op=op, b=46))


def test_ranks_last():
    ranked = registry.find_applicable(Problem(a=197, op=Operation.ADD, b=67))
    assert [t.name for t in ranked][-1] == "add_in_parts"
