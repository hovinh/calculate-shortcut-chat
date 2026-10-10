import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from quickmath import registry
from quickmath.models import Operation, Problem

consecutive = registry.get("sum_consecutive")
evens = registry.get("sum_evens")
odds = registry.get("sum_odds")


def series(a, b, step=1):
    return Problem(a=a, op=Operation.SERIES, b=b, step=step)


# ---- The series problem itself ----------------------------------------------


@pytest.mark.parametrize(
    "a, b, step, text",
    [
        (1, 100, 1, "1 + 2 + 3 + … + 100"),
        (1, 19, 2, "1 + 3 + 5 + … + 19"),
        (2, 8, 2, "2 + 4 + 6 + 8"),
    ],
)
def test_str(a, b, step, text):
    assert str(series(a, b, step)) == text


@given(st.integers(-1000, 1000), st.integers(0, 200), st.integers(1, 20))
def test_exact_matches_adding_up(a, k, step):
    b = a + k * step
    assert series(a, b, step).exact() == sum(range(a, b + 1, step))


@pytest.mark.parametrize(
    "a, b, step",
    [
        (1, 10, 2),  # 10 is not reached from 1 in steps of 2
        (10, 1, 1),  # goes downwards
        (1, 10, 0),
    ],
)
def test_invalid_series(a, b, step):
    with pytest.raises(ValidationError):
        series(a, b, step)


# ---- Shortcut 9: 1 + 2 + … + n -------------------------------------------------


def test_consecutive_worked_example():
    sol = consecutive.solve(series(1, 100))
    assert [s.expr for s in sol.steps] == ["100 × 101", "10100 ÷ 2"]
    assert [s.result for s in sol.steps] == [10100, 5050]
    assert sol.answer == 5050
    assert sol.verified


@given(st.integers(2, 10**9))
def test_consecutive_always_matches_arithmetic(n):
    assert consecutive.solve(series(1, n)).answer == n * (n + 1) // 2


# ---- Shortcut 10: first n even numbers -------------------------------------------


def test_evens_worked_example():
    sol = evens.solve(series(2, 20, 2))
    assert [s.expr for s in sol.steps] == ["20 ÷ 2", "10 × 11"]
    assert [s.result for s in sol.steps] == [10, 110]
    assert sol.answer == 110


@given(st.integers(2, 10**9))
def test_evens_always_matches_arithmetic(n):
    assert evens.solve(series(2, 2 * n, 2)).answer == series(2, 2 * n, 2).exact()


# ---- Shortcut 11: first n odd numbers --------------------------------------------


def test_odds_worked_example():
    sol = odds.solve(series(1, 19, 2))
    assert [s.expr for s in sol.steps] == ["(19 + 1) ÷ 2", "10 × 10"]
    assert [s.result for s in sol.steps] == [10, 100]
    assert sol.answer == 100


@given(st.integers(2, 10**9))
def test_odds_always_matches_arithmetic(n):
    assert odds.solve(series(1, 2 * n - 1, 2)).answer == series(1, 2 * n - 1, 2).exact()


# ---- Which shortcut applies --------------------------------------------------------


@pytest.mark.parametrize(
    "a, b, step, best",
    [
        (1, 100, 1, "sum_consecutive"),
        (2, 50, 2, "sum_evens"),
        (1, 49, 2, "sum_odds"),
    ],
)
def test_each_series_has_one_shortcut(a, b, step, best):
    assert [t.name for t in registry.find_applicable(series(a, b, step))] == [best]


@pytest.mark.parametrize(
    "a, b, step",
    [
        (2, 100, 1),  # doesn't start at 1
        (3, 21, 2),  # odd numbers not starting at 1
        (4, 20, 2),  # even numbers not starting at 2
        (1, 100, 3),
        (1, 1, 1),  # a single term
    ],
)
def test_no_series_shortcut(a, b, step):
    assert registry.find_applicable(series(a, b, step)) == []


@pytest.mark.parametrize("name", ["sum_consecutive", "sum_evens", "sum_odds"])
def test_only_series(name):
    assert not registry.get(name).applies(Problem(a=1, op=Operation.ADD, b=100))
