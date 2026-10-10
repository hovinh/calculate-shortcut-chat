import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

sub = registry.get("subtract_from_nines")

nines = st.integers(1, 12).map(lambda k: int("9" * k))


def test_worked_example():
    sol = sub.solve(Problem(a=99, op=Operation.SUBTRACT, b=18))
    assert [s.expr for s in sol.steps] == ["9 − 1", "9 − 8", "8 1"]
    assert [s.result for s in sol.steps] == [8, 1, 81]
    assert sol.answer == 81
    assert sol.verified


def test_shorter_number_is_padded_with_zeros():
    sol = sub.solve(Problem(a=999, op=Operation.SUBTRACT, b=18))
    assert "018" in sol.steps[0].say
    assert [s.result for s in sol.steps] == [9, 8, 1, 981]


def test_leading_zero_in_answer():
    sol = sub.solve(Problem(a=99, op=Operation.SUBTRACT, b=95))
    assert [s.result for s in sol.steps] == [0, 4, 4]


@given(nines.flatmap(lambda a: st.tuples(st.just(a), st.integers(0, a))))
def test_always_matches_arithmetic(ab):
    a, b = ab
    assert sub.solve(Problem(a=a, op=Operation.SUBTRACT, b=b)).answer == a - b


@pytest.mark.parametrize(
    "a, b",
    [
        (98, 18),  # not all 9s
        (18, 99),  # 9s on the wrong side
        (99, 100),  # answer would be negative
        (99, -1),
    ],
)
def test_not_applicable(a, b):
    assert not sub.applies(Problem(a=a, op=Operation.SUBTRACT, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.MULTIPLY])
def test_only_subtraction(op):
    assert not sub.applies(Problem(a=99, op=op, b=18))
