import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

mul = registry.get("multiply_by_power_of_10")

powers = st.integers(1, 12).map(lambda k: 10**k)


def test_worked_example():
    sol = mul.solve(Problem(a=47, op=Operation.MULTIPLY, b=100))
    assert [s.expr for s in sol.steps] == ["zeros in 100", "47 followed by 00"]
    assert [s.result for s in sol.steps] == [2, 4700]
    assert sol.answer == 4700
    assert sol.verified


def test_power_of_10_first():
    sol = mul.solve(Problem(a=10000, op=Operation.MULTIPLY, b=36))
    assert [s.result for s in sol.steps] == [4, 360000]


def test_both_powers_of_10():
    assert mul.solve(Problem(a=10, op=Operation.MULTIPLY, b=1000)).answer == 10000


@given(st.integers(1, 10**9), powers, st.booleans())
def test_always_matches_arithmetic(n, power, power_first):
    a, b = (power, n) if power_first else (n, power)
    assert mul.solve(Problem(a=a, op=Operation.MULTIPLY, b=b)).answer == a * b


@pytest.mark.parametrize(
    "a, b",
    [
        (47, 1),  # 1 = 10**0 has no zeros to add
        (47, 200),  # not a power of 10
        (47, 110),
        (0, 100),  # nothing to append zeros to
        (-5, 100),
    ],
)
def test_not_applicable(a, b):
    assert not mul.applies(Problem(a=a, op=Operation.MULTIPLY, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.SUBTRACT])
def test_only_multiplication(op):
    assert not mul.applies(Problem(a=470, op=op, b=100))
