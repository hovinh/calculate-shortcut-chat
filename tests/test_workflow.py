"""Agent loop tests with a scripted fake LLM (no network)."""

import json

from openai.types.chat import ChatCompletion

from quickmath.agent import FinalAnswer, ToolCall, ToolResult, TutorAgent


def completion(content=None, tool_calls=()):
    return ChatCompletion.model_validate(
        {
            "id": "x",
            "object": "chat.completion",
            "created": 0,
            "model": "fake",
            "choices": [
                {
                    "index": 0,
                    "finish_reason": "tool_calls" if tool_calls else "stop",
                    "message": {
                        "role": "assistant",
                        "content": content,
                        "tool_calls": [
                            {"id": f"call_{i}", "type": "function", "function": {"name": n, "arguments": a}}
                            for i, (n, a) in enumerate(tool_calls)
                        ]
                        or None,
                    },
                }
            ],
        }
    )


class FakeClient:
    """Mimics client.chat.completions.create, returning scripted responses in order."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.requests = []
        self.chat = self
        self.completions = self

    def create(self, **kwargs):
        self.requests.append(kwargs)
        return self.responses.pop(0)


def test_tool_round_then_answer():
    client = FakeClient(
        completion(tool_calls=[("solve_with_shortcut", json.dumps({"a": 47, "operation": "+", "b": 9}))]),
        completion(content="Add 10, take 1: **56**"),
    )
    messages = [{"role": "user", "content": "47 + 9?"}]
    events = list(TutorAgent(client, "fake").run(messages))

    assert [type(e) for e in events] == [ToolCall, ToolResult, FinalAnswer]
    assert events[1].result["solution"]["answer"] == 56
    assert events[2].text == "Add 10, take 1: **56**"
    # History: user, assistant(tool_calls), tool, assistant(answer)
    assert [m["role"] for m in messages] == ["user", "assistant", "tool", "assistant"]
    # The second request carried the tool result back to the LLM.
    assert client.requests[1]["messages"][-1]["role"] == "tool"
    assert client.requests[0]["messages"][0]["role"] == "system"


def test_bad_json_arguments_are_reported_to_llm():
    client = FakeClient(completion(tool_calls=[("solve_with_shortcut", "{not json")]), completion(content="sorry"))
    events = list(TutorAgent(client, "fake").run([{"role": "user", "content": "?"}]))
    assert "error" in events[1].result


def test_stops_after_max_rounds():
    loop = completion(tool_calls=[("list_shortcuts", "{}")])
    client = FakeClient(loop, loop, completion(content="done"))
    events = list(TutorAgent(client, "fake", max_rounds=2).run([{"role": "user", "content": "?"}]))
    assert events[-1] == FinalAnswer("done")
    assert client.requests[-1]["tool_choice"] == "none"
