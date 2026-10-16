from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from quickmath import registry
from quickmath.models import Operation, Problem

div = registry.get("divide_by_power_of_10")

powers = st.integers(1, 12).map(lambda k: 10**k)
numbers = st.integers(1, 10**9) | st.decimals(min_value="0.001", max_value="100000", places=3).filter(
    lambda d: d > 0
)


def test_worked_example():
    sol = div.solve(Problem(a=4567, op=Operation.DIVIDE, b=100))
    assert sol.problem == "4567 ÷ 100"
    assert [s.expr for s in sol.steps] == ["zeros in 100", "4567 → 45.67"]
    assert [s.result for s in sol.steps] == [2, Decimal("45.67")]
    assert sol.steps[1].say == "Put a decimal point in 4567, leaving 2 digits to its right"
    assert sol.answer == Decimal("45.67")
    assert sol.verified


def test_decimal_point_moves_left():
    sol = div.solve(Problem(a=45.6, op=Operation.DIVIDE, b=10))
    assert sol.steps[1].say == "Move the decimal point in 45.6 1 place to the left"
    assert sol.steps[1].expr == "45.6 → 4.56"
    assert sol.answer == Decimal("4.56")


@pytest.mark.parametrize(
    "a, b, expr",
    [
        (7, 100, "7 → 0.07"),
        (45.6, 1000, "45.6 → 0.0456"),
        (0.5, 10, "0.5 → 0.05"),
    ],
)
def test_fills_with_zeros_when_digits_run_out(a, b, expr):
    sol = div.solve(Problem(a=a, op=Operation.DIVIDE, b=b))
    assert "filling the empty places after the point with zeros" in sol.steps[1].say
    assert sol.steps[1].expr == expr


@pytest.mark.parametrize("a, b", [(45, 100), (4567, 10), (45.6, 100)])
def test_no_zeros_to_fill(a, b):
    assert "filling" not in div.solve(Problem(a=a, op=Operation.DIVIDE, b=b)).steps[1].say


def test_drops_zeros_at_the_end():
    sol = div.solve(Problem(a=4500, op=Operation.DIVIDE, b=100))
    assert sol.steps[1].say.endswith("then drop the zeros at the end")
    assert sol.steps[1].expr == "4500 → 45.00 = 45"
    assert sol.answer == 45


@given(numbers, powers)
def test_always_matches_arithmetic(n, power):
    assert div.solve(Problem(a=n, op=Operation.DIVIDE, b=power)).answer == Decimal(n) / power


@pytest.mark.parametrize(
    "a, b",
    [
        (100, 4567),  # the number being divided must be the other one
        (4567, 1),
        (4567, 200),
        (4567, 0.1),
        (-4567, 100),
        (0, 100),
    ],
)
def test_not_applicable(a, b):
    assert not div.applies(Problem(a=a, op=Operation.DIVIDE, b=b))


@pytest.mark.parametrize("op", [Operation.ADD, Operation.SUBTRACT, Operation.MULTIPLY])
def test_only_division(op):
    assert not div.applies(Problem(a=4567, op=op, b=100))
