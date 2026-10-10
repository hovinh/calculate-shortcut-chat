import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

add_nines = registry.get("add_nines")

nines = st.integers(1, 12).map(lambda k: int("9" * k))


def test_worked_example_99():
    sol = add_nines.solve(Problem(a=47, op=Operation.ADD, b=99))
    assert [s.expr for s in sol.steps] == ["47 + 100", "147 − 1"]
    assert [s.result for s in sol.steps] == [147, 146]
    assert sol.answer == 146
    assert sol.verified


def test_worked_example_999():
    sol = add_nines.solve(Problem(a=999, op=Operation.ADD, b=356))
    assert sol.steps[0].expr == "356 + 1000"
    assert sol.answer == 1355


@given(st.integers(-10**6, 10**6), nines, st.booleans())
def test_always_matches_arithmetic(n, k, nines_first):
    a, b = (k, n) if nines_first else (n, k)
    assert add_nines.solve(Problem(a=a, op=Operation.ADD, b=b)).answer == n + k


@pytest.mark.parametrize("x", [0, 98, 90, 199, 909, -9, -99])
def test_not_applicable_without_all_nines(x):
    assert not add_nines.applies(Problem(a=47, op=Operation.ADD, b=x))


@pytest.mark.parametrize("op", [Operation.SUBTRACT, Operation.MULTIPLY])
def test_only_addition(op):
    assert not add_nines.applies(Problem(a=47, op=op, b=99))


def test_ranks_below_add_9():
    ranked = registry.find_applicable(Problem(a=47, op=Operation.ADD, b=9))
    assert [t.name for t in ranked] == ["add_9", "add_nines"]
