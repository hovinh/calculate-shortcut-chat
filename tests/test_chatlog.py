import json

from quickmath.chatlog import ChatLog


def read(log):
    return json.loads(log.path.read_text(encoding="utf-8"))


def test_nothing_written_before_first_turn(tmp_path):
    log = ChatLog(tmp_path / "logs", model="fake")
    assert not log.path.exists()


def test_turns_are_saved(tmp_path):
    log = ChatLog(tmp_path, model="fake")
    calls = [{"name": "solve_with_shortcut", "arguments": {"a": 47, "operation": "+", "b": 9}, "result": {"found": True}}]
    assert log.add_turn("What is 47 + 9?", calls, answer="**56**") == 1
    assert log.add_turn("And 10 + 10?", [], error="APIError: boom") == 2

    data = read(log)
    assert data["model"] == "fake"
    assert [t["turn"] for t in data["turns"]] == [1, 2]
    assert data["turns"][0]["question"] == "What is 47 + 9?"
    assert data["turns"][0]["tool_calls"] == calls
    assert data["turns"][0]["answer"] == "**56**"
    assert data["turns"][1]["error"] == "APIError: boom"
    assert data["turns"][1]["answer"] is None


def test_feedback(tmp_path):
    log = ChatLog(tmp_path, model="fake")
    log.add_turn("What is 47 + 9?", [], answer="56")

    log.set_feedback(1, "down", "  Should mention the add-10 trick  ")
    assert read(log)["turns"][0]["feedback"] == {"rating": "down", "note": "Should mention the add-10 trick"}

    log.set_feedback(1, None, "")
    assert read(log)["turns"][0]["feedback"] is None


def test_unicode_kept_readable(tmp_path):
    log = ChatLog(tmp_path, model="fake")
    log.add_turn("1 + 2 + … + 100", [], answer="5050")
    assert "1 + 2 + … + 100" in log.path.read_text(encoding="utf-8")
