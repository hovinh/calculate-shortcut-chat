import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

split = registry.get("split_to_round")


def test_worked_example():
    sol = split.solve(Problem(a=197, op=Operation.ADD, b=67))
    assert [s.expr for s in sol.steps] == ["67 − 3", "197 + 3", "200 + 64"]
    assert [s.result for s in sol.steps] == [64, 200, 264]
    assert sol.answer == 264
    assert sol.verified


def test_order_does_not_matter():
    sol = split.solve(Problem(a=67, op=Operation.ADD, b=197))
    assert sol.steps[1].expr == "197 + 3"
    assert sol.answer == 264


@pytest.mark.parametrize(
    "a, b, target",
    [
        (1996, 45, 2000),
        (197, 98, 200),  # both close: the larger one is rounded
    ],
)
def test_round_number_chosen(a, b, target):
    sol = split.solve(Problem(a=a, op=Operation.ADD, b=b))
    assert sol.steps[1].result == target


# A number just below a multiple of 100, e.g. 197 or 1991.
near_hundred = st.tuples(st.integers(1, 10**7), st.integers(1, 9)).map(lambda t: t[0] * 100 - t[1])


@given(near_hundred.flatmap(lambda n: st.tuples(st.just(n), st.integers(10, n))), st.booleans())
def test_always_matches_arithmetic(near_other, near_first):
    near, other = near_other
    a, b = (near, other) if near_first else (other, near)
    p = Problem(a=a, op=Operation.ADD, b=b)
    assert split.applies(p)
    assert split.solve(p).answer == a + b


@pytest.mark.parametrize(
    "a, b",
    [
        (200, 67),  # already a multiple of 100
        (98, 145),  # the close number is the smaller one
        (203, 45),  # just above a hundred, not below
        (47, 8),  # only close to a multiple of 10
        (190, 30),  # 10 short of 200 is too far
        (195, 3),  # 195 -> 200 needs 5, only 3 to give
        (197, 3),  # nothing left after filling the gap
        (-3, 47),
    ],
)
def test_not_applicable(a, b):
    assert not split.applies(Problem(a=a, op=Operation.ADD, b=b))


@pytest.mark.parametrize("op", [Operation.SUBTRACT, Operation.MULTIPLY])
def test_only_addition(op):
    assert not split.applies(Problem(a=197, op=op, b=67))


def test_ranks_below_nines_tricks():
    ranked = registry.find_applicable(Problem(a=47, op=Operation.ADD, b=99))
    assert [t.name for t in ranked] == ["add_nines", "split_to_round", "round_and_compensate", "add_in_parts"]
