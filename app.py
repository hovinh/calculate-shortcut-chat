"""Streamlit chat UI.  Run with:  streamlit run app.py"""

from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st

from quickmath import tools
from quickmath.agent import ConfigError, FinalAnswer, ToolCall, ToolResult, TutorAgent, load_client
from quickmath.chatlog import ChatLog

LOG_DIR = Path(os.getenv("QUICKMATH_LOG_DIR") or Path(__file__).parent / "logs")

EXAMPLES = [
    "What is 47 + 9?",
    "How do I add 9 + 386 quickly?",
    "Work out 120 + 9 + 9",
    "Add up 1 + 2 + … + 100",
    "What is 47 × 1000?",
    "What shortcuts do you know?",
]

st.set_page_config(page_title="Quick Math Coach", page_icon="🧮")


@st.cache_resource
def get_agent() -> TutorAgent:
    client, model = load_client()
    return TutorAgent(client, model)


def trace_label(n_calls: int) -> str:
    return f"Agent used {n_calls} tool call{'s' if n_calls != 1 else ''}" if n_calls else "Agent answered without tools"


def feedback_widget(log: ChatLog, turn: int) -> None:
    """👍/👎 and an optional note under an answer, saved into the session log."""
    rating_key, note_key = f"rating_{log.path.stem}_{turn}", f"note_{log.path.stem}_{turn}"

    def save() -> None:
        rating = {0: "down", 1: "up"}.get(st.session_state.get(rating_key))
        log.set_feedback(turn, rating, st.session_state.get(note_key, ""))

    st.feedback("thumbs", key=rating_key, on_change=save)
    if st.session_state.get(rating_key) is not None:
        st.text_input("Feedback note (optional)", key=note_key, on_change=save, placeholder="What should change?")


def render_history(messages: list[dict], log: ChatLog, turn_ids: list[int]) -> None:
    """Show past turns: user bubble, then one assistant bubble with the tool trace + answer."""
    i = 0
    n_questions = 0
    while i < len(messages):
        if messages[i]["role"] == "user":
            st.chat_message("user").markdown(messages[i]["content"])
            i += 1
            n_questions += 1
            continue
        # Collect the assistant turn: tool-call rounds followed by the final reply.
        calls, results, answer = [], {}, ""
        while i < len(messages) and messages[i]["role"] != "user":
            m = messages[i]
            if m["role"] == "tool":
                results[m["tool_call_id"]] = json.loads(m["content"])
            elif m.get("tool_calls"):
                calls += m["tool_calls"]
            else:
                answer = m["content"]
            i += 1
        with st.chat_message("assistant"):
            if show_trace and calls:
                with st.expander(trace_label(len(calls))):
                    for c in calls:
                        st.markdown(f"🔧 **{c['function']['name']}** `{c['function']['arguments']}`")
                        st.json(results.get(c["id"], {}), expanded=False)
            st.markdown(answer)
            feedback_widget(log, turn_ids[n_questions - 1])


# ---- Sidebar -------------------------------------------------------------
with st.sidebar:
    st.header("🧮 Quick Math Coach")
    st.caption("An LLM agent that calls verified Python tools to teach mental-math shortcuts.")
    show_trace = st.toggle("Show agent trace", value=True)

    st.subheader("Try an example")
    for ex in EXAMPLES:
        if st.button(ex, use_container_width=True):
            st.session_state.pending = ex

    st.subheader("Known shortcuts")
    for s in tools.list_shortcuts()["shortcuts"]:
        st.markdown(f"**{s['title']}** (`{s['operation']}`)  \n{s['rule']}")

    if st.button("Clear chat", type="secondary"):
        # A fresh chat gets a fresh log file.
        for key in ("messages", "turn_ids", "log"):
            st.session_state.pop(key, None)

# ---- Chat ----------------------------------------------------------------
st.title("Quick Math Coach")

try:
    agent = get_agent()
except ConfigError as e:
    st.error(f"LLM is not configured: {e}\n\nCopy `.env.example` to `.env` and fill it in.")
    st.stop()

messages: list[dict] = st.session_state.setdefault("messages", [])
# Log turn number for each answered question in `messages` (failed turns are logged but not kept in the chat).
turn_ids: list[int] = st.session_state.setdefault("turn_ids", [])
if "log" not in st.session_state:
    st.session_state.log = ChatLog(LOG_DIR, agent.model)
log: ChatLog = st.session_state.log

with st.sidebar:
    st.caption(f"📝 This chat is logged to `{log.path}` after each answer, with any 👍/👎 feedback.")

render_history(messages, log, turn_ids)

prompt = st.chat_input("Ask me a calculation, e.g. 47 + 9") or st.session_state.pop("pending", None)
if prompt:
    st.chat_message("user").markdown(prompt)
    messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        status = st.status("Thinking…", expanded=show_trace) if show_trace else None
        calls: dict[str, dict] = {}  # tool call id -> name, arguments, result
        try:
            for event in agent.run(messages):
                match event:
                    case ToolCall(id=call_id, name=name, arguments=args):
                        calls[call_id] = {"name": name, "arguments": args}
                        if status:
                            status.markdown(f"🔧 **{name}** `{json.dumps(args)}`")
                    case ToolResult(id=call_id, result=result):
                        calls[call_id]["result"] = result
                        if status:
                            status.json(result, expanded=False)
                    case FinalAnswer(text=text):
                        if status:
                            status.update(label=trace_label(len(calls)), state="complete", expanded=False)
                        st.markdown(text)
                        turn_ids.append(log.add_turn(prompt, list(calls.values()), answer=text))
                        feedback_widget(log, turn_ids[-1])
        except Exception as e:  # surface API errors in the chat instead of a stack trace
            if status:
                status.update(label="Error", state="error")
            st.error(f"{type(e).__name__}: {e}")
            log.add_turn(prompt, list(calls.values()), error=f"{type(e).__name__}: {e}")
            # Drop the unanswered turn so history stays valid for the next request.
            while messages and messages[-1]["role"] != "user":
                messages.pop()
            messages.pop()
