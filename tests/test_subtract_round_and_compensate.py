import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

src = registry.get("subtract_round_and_compensate")

# A number within 9 of a multiple of 100 (but not one), e.g. 98, 103, 1991.
near_hundred = st.tuples(st.integers(1, 10**7), st.integers(-9, 9).filter(bool)).map(lambda t: t[0] * 100 + t[1])


def test_worked_example_subtract_more():
    sol = src.solve(Problem(a=176, op=Operation.SUBTRACT, b=98))
    assert [s.expr for s in sol.steps] == ["176 − 100", "76 + 2"]
    assert [s.result for s in sol.steps] == [76, 78]
    assert sol.answer == 78
    assert sol.verified


def test_subtract_less():
    sol = src.solve(Problem(a=176, op=Operation.SUBTRACT, b=103))
    assert [s.expr for s in sol.steps] == ["176 − 100", "76 − 3"]
    assert sol.answer == 73


def test_larger_round_number():
    sol = src.solve(Problem(a=1234, op=Operation.SUBTRACT, b=496))
    assert [s.expr for s in sol.steps] == ["1234 − 500", "734 + 4"]
    assert sol.answer == 738


@given(near_hundred.flatmap(lambda b: st.tuples(st.integers(b + 9, 10**10), st.just(b))))
def test_always_matches_arithmetic(ab):
    a, b = ab
    p = Problem(a=a, op=Operation.SUBTRACT, b=b)
    assert src.applies(p)
    assert src.solve(p).answer == a - b


@pytest.mark.parametrize(
    "a, b",
    [
        (176, 200),  # already a multiple of 100
        (176, 90),  # 10 away is too far
        (176, 47),
        (176, 3),  # 3 is near 0, which doesn't help
        (98, 176),  # close number on the wrong side
        (99, 98),  # 100 doesn't fit within 99
        (100, 103),  # answer would be negative
        (176, -98),
    ],
)
def test_not_applicable(a, b):
    assert not src.applies(Problem(a=a, op=Operation.SUBTRACT, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.MULTIPLY])
def test_only_subtraction(op):
    assert not src.applies(Problem(a=176, op=op, b=98))


@pytest.mark.parametrize(
    "a, b, best",
    [
        (176, 98, "subtract_round_and_compensate"),
        (100, 98, "subtract_from_power_of_10"),
        (999, 101, "subtract_from_nines"),
    ],
)
def test_ranking(a, b, best):
    assert registry.find_applicable(Problem(a=a, op=Operation.SUBTRACT, b=b))[0].name == best
