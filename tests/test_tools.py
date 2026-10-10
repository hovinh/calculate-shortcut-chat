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
    assert "error" in tools.dispatch("solve_with_shortcut", {"a": 1, "operation": "/", "b": 9})
    assert "error" in tools.dispatch("nope", {})


def test_list_shortcuts():
    names = [s["name"] for s in tools.dispatch("list_shortcuts", {})["shortcuts"]]
    assert "add_9" in names
