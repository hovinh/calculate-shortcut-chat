"""Drive the Streamlit page headlessly with a fake LLM."""

import json

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

import quickmath.agent
from test_workflow import FakeClient, completion


@pytest.fixture
def fake_llm(monkeypatch):
    client = FakeClient(
        completion(tool_calls=[("solve_with_shortcut", json.dumps({"a": 47, "operation": "+", "b": 9}))]),
        completion(content="Add 10, take 1: **56**"),
    )
    monkeypatch.setattr(quickmath.agent, "load_client", lambda: (client, "fake"))
    st.cache_resource.clear()
    yield client
    st.cache_resource.clear()


def test_chat_round_trip(fake_llm):
    at = AppTest.from_file("../app.py", default_timeout=10).run()
    assert not at.exception

    at.chat_input[0].set_value("What is 47 + 9?").run()
    assert not at.exception
    assert "Add 10, take 1: **56**" in [m.value for m in at.main.markdown]
    assert [m["role"] for m in at.session_state.messages] == ["user", "assistant", "tool", "assistant"]
