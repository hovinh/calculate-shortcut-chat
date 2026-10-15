from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

mul = registry.get("multiply_decimal_by_power_of_10")

powers = st.integers(1, 12).map(lambda k: 10**k)
decimals = st.decimals(min_value="0.001", max_value="100000", places=3).filter(lambda d: d != d.to_integral_value())


def test_worked_example():
    sol = mul.solve(Problem(a=3.75, op=Operation.MULTIPLY, b=100))
    assert sol.problem == "3.75 × 100"
    assert [s.expr for s in sol.steps] == ["zeros in 100", "3.75 → 375"]
    assert [s.result for s in sol.steps] == [2, 375]
    assert sol.answer == 375
    assert sol.verified


def test_decimal_point_stays_inside():
    sol = mul.solve(Problem(a=10, op=Operation.MULTIPLY, b=4.725))
    assert sol.steps[1].expr == "4.725 → 47.25"
    assert sol.answer == Decimal("47.25")


def test_fills_with_zeros_when_digits_run_out():
    sol = mul.solve(Problem(a=4.7, op=Operation.MULTIPLY, b=1000))
    assert "filling the empty places with zeros" in sol.steps[1].say
    assert sol.steps[1].expr == "4.7 → 4700"
    assert sol.answer == 4700


def test_small_decimal_shown_without_scientific_notation():
    sol = mul.solve(Problem(a="0.0000001", op=Operation.MULTIPLY, b=10))
    assert sol.steps[1].expr == "0.0000001 → 0.000001"


@given(decimals, powers, st.booleans())
def test_always_matches_arithmetic(n, power, power_first):
    a, b = (power, n) if power_first else (n, power)
    assert mul.solve(Problem(a=a, op=Operation.MULTIPLY, b=b)).answer == n * power


@pytest.mark.parametrize(
    "a, b",
    [
        (47, 100),  # whole numbers: that's multiply_by_power_of_10
        (4.7, 1),
        (4.7, 200),
        (4.7, 0.1),
        (-4.7, 100),
    ],
)
def test_not_applicable(a, b):
    assert not mul.applies(Problem(a=a, op=Operation.MULTIPLY, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.SUBTRACT])
def test_only_multiplication(op):
    assert not mul.applies(Problem(a=4.7, op=op, b=100))


def test_whole_number_shortcuts_skip_decimals():
    names = [t.name for t in registry.find_applicable(Problem(a=4.7, op=Operation.MULTIPLY, b=100))]
    assert names == ["multiply_decimal_by_power_of_10"]
    assert registry.find_applicable(Problem(a=4.5, op=Operation.ADD, b=9)) == []
