import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

add_9 = registry.get("add_9")


def test_worked_example():
    sol = add_9.solve(Problem(a=47, op=Operation.ADD, b=9))
    assert [s.result for s in sol.steps] == [57, 56]
    assert sol.answer == 56
    assert sol.verified


def test_9_on_the_left():
    sol = add_9.solve(Problem(a=9, op=Operation.ADD, b=47))
    assert sol.steps[0].expr == "47 + 10"
    assert sol.answer == 56


@given(st.integers(-10**6, 10**6), st.booleans())
def test_always_matches_arithmetic(n, nine_first):
    a, b = (9, n) if nine_first else (n, 9)
    assert add_9.solve(Problem(a=a, op=Operation.ADD, b=b)).answer == n + 9


@given(st.integers(), st.integers().filter(lambda x: x != 9))
def test_not_applicable_without_9(a, b):
    assert not add_9.applies(Problem(a=a if a != 9 else 8, op=Operation.ADD, b=b))


@pytest.mark.parametrize("op", [Operation.SUBTRACT, Operation.MULTIPLY])
def test_only_addition(op):
    assert not add_9.applies(Problem(a=47, op=op, b=9))
