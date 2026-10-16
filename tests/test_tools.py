import json

from quickmath import tools


def test_specs_are_json_serializable():
    json.dumps(tools.tool_specs())


def test_picks_shortcut_automatically():
    out = tools.dispatch("solve_with_shortcut", {"a": 47, "operation": "+", "b": 9})
    assert out["found"]
    assert out["solution"]["technique"] == "add_9"
    assert out["solution"]["answer"] == 56
    assert out["other_applicable_shortcuts"] == ["add_nines"]


def test_picks_add_nines_for_99():
    out = tools.dispatch("solve_with_shortcut", {"a": 47, "operation": "+", "b": 99})
    assert out["solution"]["technique"] == "add_nines"
    assert out["solution"]["answer"] == 146


def test_multiply_by_power_of_10():
    out = tools.dispatch("solve_with_shortcut", {"a": 47, "operation": "*", "b": 100})
    assert out["solution"]["technique"] == "multiply_by_power_of_10"
    assert out["solution"]["problem"] == "47 × 100"
    assert out["solution"]["answer"] == 4700


def test_multiply_decimal_by_power_of_10():
    out = tools.dispatch("solve_with_shortcut", {"a": 3.75, "operation": "*", "b": 10})
    assert out["solution"]["technique"] == "multiply_decimal_by_power_of_10"
    assert out["solution"]["answer"] == 37.5
    json.dumps(out)  # decimals must reach the LLM as plain JSON numbers


def test_divide_by_power_of_10():
    out = tools.dispatch("solve_with_shortcut", {"a": 4567, "operation": "/", "b": 100})
    assert out["solution"]["technique"] == "divide_by_power_of_10"
    assert out["solution"]["problem"] == "4567 ÷ 100"
    assert out["solution"]["answer"] == 45.67
    json.dumps(out)


def test_division_without_shortcut_still_returns_answer():
    out = tools.dispatch("solve_with_shortcut", {"a": 7, "operation": "/", "b": 4})
    assert not out["found"]
    assert out["answer"] == 1.75


def test_divide_by_zero_returns_error():
    out = tools.dispatch("solve_with_shortcut", {"a": 7, "operation": "/", "b": 0})
    assert "divide by zero" in out["error"]


def test_decimal_without_shortcut_still_returns_answer():
    out = tools.dispatch("solve_with_shortcut", {"a": 0.1, "operation": "+", "b": 0.2})
    assert out["answer"] == 0.3  # exact, not 0.30000000000000004
    json.dumps(out)


def test_series_must_be_whole_numbers():
    out = tools.dispatch("solve_with_shortcut", {"a": 0.5, "operation": "series", "b": 10.5})
    assert "whole-number" in out["error"]


def test_series():
    out = tools.dispatch("solve_with_shortcut", {"a": 1, "operation": "series", "b": 19, "step": 2})
    assert out["solution"]["technique"] == "sum_odds"
    assert out["solution"]["problem"] == "1 + 3 + 5 + … + 19"
    assert out["solution"]["answer"] == 100


def test_series_step_defaults_to_1():
    out = tools.dispatch("solve_with_shortcut", {"a": 1, "operation": "series", "b": 100})
    assert out["solution"]["answer"] == 5050


def test_invalid_series_returns_error():
    out = tools.dispatch("solve_with_shortcut", {"a": 1, "operation": "series", "b": 10, "step": 2})
    assert "not reached" in out["error"]


def test_no_shortcut_still_returns_answer():
    out = tools.dispatch("solve_with_shortcut", {"a": 150, "operation": "+", "b": 60})
    assert out == {
        "problem": "150 + 60",
        "found": False,
        "answer": 210,
        "message": "No known shortcut applies to this problem.",
    }


def test_explicit_technique_that_does_not_apply():
    out = tools.dispatch("solve_with_shortcut", {"a": 150, "operation": "+", "b": 60, "technique": "add_9"})
    assert not out["found"]
    assert out["applicable_shortcuts"] == []


def test_bad_arguments_return_error():
    assert "error" in tools.dispatch("solve_with_shortcut", {"a": "abc", "operation": "+", "b": 9})
    assert "error" in tools.dispatch("solve_with_shortcut", {"a": 1, "operation": "%", "b": 9})
    assert "error" in tools.dispatch("nope", {})


def test_list_shortcuts():
    names = [s["name"] for s in tools.dispatch("list_shortcuts", {})["shortcuts"]]
    assert "add_9" in names
