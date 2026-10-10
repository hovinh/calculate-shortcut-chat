"""The agent loop: LLM -> tool calls -> tool results -> LLM ... -> final answer.

Each round the LLM either asks for tools (we run them and send the results back)
or decides it has enough information and replies. `run` yields an event at each
stage so a UI can show the agent's reasoning trail as it happens.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from quickmath import tools
from quickmath.agent.prompts import SYSTEM_PROMPT


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ToolResult:
    id: str
    name: str
    result: dict[str, Any]


@dataclass
class FinalAnswer:
    text: str


Event = ToolCall | ToolResult | FinalAnswer


class TutorAgent:
    def __init__(self, client: OpenAI, model: str, max_rounds: int = 5):
        self.client = client
        self.model = model
        self.max_rounds = max_rounds

    def run(self, messages: list[dict[str, Any]]) -> Iterator[Event]:
        """Continue the conversation in `messages` (OpenAI chat format, no system message).

        New assistant and tool messages are appended to `messages` in place, so the
        caller keeps the full history for follow-up questions.
        """
        for _ in range(self.max_rounds):
            msg = self._complete(messages, tool_choice="auto")

            if not msg.tool_calls:  # the LLM decided it has enough to answer
                messages.append({"role": "assistant", "content": msg.content or ""})
                yield FinalAnswer(msg.content or "")
                return

            messages.append(
                {
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": [
                        {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                        for tc in msg.tool_calls
                    ],
                }
            )
            for tc in msg.tool_calls:
                yield from self._run_tool(tc.id, tc.function.name, tc.function.arguments, messages)

        # Out of rounds: make the LLM answer with what it has, no more tools.
        msg = self._complete(messages, tool_choice="none")
        messages.append({"role": "assistant", "content": msg.content or ""})
        yield FinalAnswer(msg.content or "")

    def _complete(self, messages: list[dict[str, Any]], tool_choice: str):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
            tools=tools.tool_specs(),
            tool_choice=tool_choice,
        )
        return response.choices[0].message

    def _run_tool(self, call_id: str, name: str, raw_args: str, messages: list[dict[str, Any]]) -> Iterator[Event]:
        try:
            args = json.loads(raw_args or "{}")
        except json.JSONDecodeError:
            args = {}
            result = {"error": f"Arguments were not valid JSON: {raw_args!r}"}
        else:
            result = tools.dispatch(name, args)

        yield ToolCall(call_id, name, args)
        messages.append({"role": "tool", "tool_call_id": call_id, "content": json.dumps(result, ensure_ascii=False)})
        yield ToolResult(call_id, name, result)
