import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

sub = registry.get("subtract_from_power_of_10")

powers = st.integers(1, 12).map(lambda k: 10**k)


def test_worked_example():
    sol = sub.solve(Problem(a=100, op=Operation.SUBTRACT, b=18))
    assert [s.expr for s in sol.steps] == ["100 − 1", "9 − 1", "9 − 8", "8 1", "81 + 1"]
    assert [s.result for s in sol.steps] == [99, 8, 1, 81, 82]
    assert sol.answer == 82
    assert sol.verified


def test_shorter_number_is_padded_with_zeros():
    sol = sub.solve(Problem(a=1000, op=Operation.SUBTRACT, b=18))
    assert [s.result for s in sol.steps] == [999, 9, 8, 1, 981, 982]


@given(powers.flatmap(lambda a: st.tuples(st.just(a), st.integers(0, a - 1))))
def test_always_matches_arithmetic(ab):
    a, b = ab
    assert sub.solve(Problem(a=a, op=Operation.SUBTRACT, b=b)).answer == a - b


@pytest.mark.parametrize(
    "a, b",
    [
        (1, 0),  # 1 = 10**0 has no 9s to borrow from
        (200, 18),  # not a power of 10
        (110, 18),
        (18, 100),  # power of 10 on the wrong side
        (100, 100),  # b must be smaller than a
        (100, -1),
    ],
)
def test_not_applicable(a, b):
    assert not sub.applies(Problem(a=a, op=Operation.SUBTRACT, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.MULTIPLY])
def test_only_subtraction(op):
    assert not sub.applies(Problem(a=100, op=op, b=18))
