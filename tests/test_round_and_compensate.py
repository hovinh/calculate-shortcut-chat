import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

rc = registry.get("round_and_compensate")

# A number within 9 of a multiple of 100 (but not one), e.g. 97, 103, 1991.
near_hundred = st.tuples(st.integers(1, 10**7), st.integers(-9, 9).filter(bool)).map(lambda t: t[0] * 100 + t[1])


def test_worked_example_add_more():
    sol = rc.solve(Problem(a=459, op=Operation.ADD, b=97))
    assert [s.expr for s in sol.steps] == ["459 + 100", "559 − 3"]
    assert [s.result for s in sol.steps] == [559, 556]
    assert sol.answer == 556
    assert sol.verified


def test_add_less():
    sol = rc.solve(Problem(a=459, op=Operation.ADD, b=103))
    assert [s.expr for s in sol.steps] == ["459 + 100", "559 + 3"]
    assert sol.answer == 562


def test_order_does_not_matter():
    sol = rc.solve(Problem(a=97, op=Operation.ADD, b=459))
    assert sol.steps[0].expr == "459 + 100"


def test_both_close_rounds_the_smaller_adjustment():
    sol = rc.solve(Problem(a=197, op=Operation.ADD, b=98))
    assert sol.steps[0].expr == "197 + 100"


@given(near_hundred, st.integers(1, 10**9), st.booleans())
def test_always_matches_arithmetic(near, other, near_first):
    a, b = (near, other) if near_first else (other, near)
    assert rc.solve(Problem(a=a, op=Operation.ADD, b=b)).answer == a + b


@pytest.mark.parametrize(
    "a, b",
    [
        (459, 200),  # already a multiple of 100
        (459, 90),  # 10 away is too far
        (459, 47),
        (3, 47),  # 3 is near 0, which doesn't help
        (-97, 459),
    ],
)
def test_not_applicable(a, b):
    assert not rc.applies(Problem(a=a, op=Operation.ADD, b=b))


@pytest.mark.parametrize("op", [Operation.SUBTRACT, Operation.MULTIPLY])
def test_only_addition(op):
    assert not rc.applies(Problem(a=459, op=op, b=97))


@pytest.mark.parametrize(
    "a, b, best",
    [
        (459, 97, "round_and_compensate"),  # smaller number is the close one
        (459, 103, "round_and_compensate"),  # close from above
        (197, 67, "split_to_round"),  # larger number just below a hundred
        (459, 99, "add_nines"),
    ],
)
def test_ranking(a, b, best):
    assert registry.find_applicable(Problem(a=a, op=Operation.ADD, b=b))[0].name == best
