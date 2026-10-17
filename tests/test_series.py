import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from quickmath import registry
from quickmath.models import Operation, Problem

consecutive = registry.get("sum_consecutive")
evens = registry.get("sum_evens")
odds = registry.get("sum_odds")
from_a = registry.get("sum_consecutive_from_a")
arithmetic = registry.get("sum_arithmetic_series")


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


# ---- Shortcut 30: a + (a + 1) + … + b ---------------------------------------------


def test_from_a_worked_example():
    sol = from_a.solve(series(11, 20))
    assert sol.problem == "11 + 12 + 13 + … + 20"
    assert [s.say for s in sol.steps] == [
        "Square the last number, 20",
        "Square the first number, 11",
        "Take 121 away from 400",
        "Add the first and last numbers, 11 and 20",
        "Then halve it",
    ]
    assert [s.expr for s in sol.steps] == ["20 × 20", "11 × 11", "400 − 121", "279 + 11 + 20", "310 ÷ 2"]
    assert [s.result for s in sol.steps] == [400, 121, 279, 310, 155]
    assert sol.answer == 155
    assert sol.verified


@given(st.integers(2, 10**6), st.integers(1, 10**6))
def test_from_a_always_matches_arithmetic(a, k):
    assert from_a.solve(series(a, a + k)).answer == series(a, a + k).exact()


# ---- Shortcut 31: a series that goes up by the same difference ---------------------


def test_arithmetic_worked_example():
    sol = arithmetic.solve(series(2, 32, 3))
    assert sol.problem == "2 + 5 + 8 + … + 32"
    assert [s.say for s in sol.steps] == [
        "Count the numbers: take the first from the last, divide by the difference, 3, and add 1",
        "Add the first and last numbers and halve it",
        "Multiply them",
    ]
    assert [s.expr for s in sol.steps] == ["(32 − 2) ÷ 3 + 1", "(2 + 32) ÷ 2", "11 × 17"]
    assert [s.result for s in sol.steps] == [11, 17, 187]
    assert sol.answer == 187
    assert sol.verified


def test_arithmetic_odd_ends_halve_the_count():
    sol = arithmetic.solve(series(2, 35, 3))
    assert [s.say for s in sol.steps][1:] == [
        "Add the first and last numbers",
        "37 is odd, so halve the count instead",
        "Multiply them",
    ]
    assert [s.expr for s in sol.steps] == ["(35 − 2) ÷ 3 + 1", "2 + 35", "12 ÷ 2", "6 × 37"]
    assert sol.answer == 222


def test_arithmetic_negative_start():
    sol = arithmetic.solve(series(-5, 10, 1))
    assert [s.expr for s in sol.steps] == ["(10 − -5) ÷ 1 + 1", "-5 + 10", "16 ÷ 2", "8 × 5"]
    assert sol.answer == 40


@given(st.integers(-10**6, 10**6), st.integers(1, 10**4), st.integers(1, 1000))
def test_arithmetic_always_matches_arithmetic(a, k, step):
    b = a + k * step
    assert arithmetic.solve(series(a, b, step)).answer == series(a, b, step).exact()


# ---- Which shortcut applies --------------------------------------------------------


@pytest.mark.parametrize(
    "a, b, step, best",
    [
        (1, 100, 1, "sum_consecutive"),
        (2, 50, 2, "sum_evens"),
        (1, 49, 2, "sum_odds"),
        (2, 100, 1, "sum_consecutive_from_a"),
        (11, 20, 1, "sum_consecutive_from_a"),
    ],
)
def test_narrow_series_shortcut_ranks_first(a, b, step, best):
    assert [t.name for t in registry.find_applicable(series(a, b, step))] == [best, "sum_arithmetic_series"]


@pytest.mark.parametrize(
    "a, b, step",
    [
        (0, 100, 1),  # starts at 0, not a positive number
        (-5, 10, 1),  # starts below 0
        (3, 21, 2),  # odd numbers not starting at 1
        (4, 20, 2),  # even numbers not starting at 2
        (2, 32, 3),
    ],
)
def test_only_arithmetic_series(a, b, step):
    assert [t.name for t in registry.find_applicable(series(a, b, step))] == ["sum_arithmetic_series"]


@pytest.mark.parametrize("a, b, step", [(1, 1, 1), (7, 7, 3)])
def test_no_shortcut_for_a_single_term(a, b, step):
    assert registry.find_applicable(series(a, b, step)) == []


@pytest.mark.parametrize(
    "name", ["sum_consecutive", "sum_evens", "sum_odds", "sum_consecutive_from_a", "sum_arithmetic_series"]
)
def test_only_series(name):
    assert not registry.get(name).applies(Problem(a=1, op=Operation.ADD, b=100))
