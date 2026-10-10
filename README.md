# Quick Math Coach

A chatbot that teaches mental-math shortcuts. It demonstrates how to combine an
**LLM agent loop** with **tool calling**: the LLM understands the question and
explains the answer, while deterministic Python tools do (and verify) the maths.

## Architecture

```mermaid
flowchart LR
    U[User] -->|question| UI[Streamlit<br/>app.py]
    UI --> A[Agent loop<br/>agent/workflow.py]
    A -->|messages + tool specs| LLM[(Azure OpenAI)]
    LLM -->|tool_calls| A
    A -->|dispatch| T[Tools<br/>tools.py]
    T --> R[Registry<br/>picks best shortcut]
    R --> S[Techniques<br/>techniques/*.py]
    S -->|verified steps| A
    LLM -->|final answer| A --> UI
```

| Layer | File | Responsibility |
|---|---|---|
| Techniques | `src/quickmath/techniques/` | One class per shortcut: when it applies, and its steps. Every result is checked against plain arithmetic. |
| Registry | `src/quickmath/registry.py` | Finds the applicable techniques and ranks them by `priority`. |
| Tools | `src/quickmath/tools.py` | Exposes the registry to the LLM as two function-calling tools: `solve_with_shortcut` and `list_shortcuts`. |
| Agent | `src/quickmath/agent/workflow.py` | The loop: call LLM, run requested tools, feed results back, repeat until the LLM answers (max 5 rounds). Yields events so the UI can show each step. |
| UI | `app.py` | Chat interface with a live, collapsible agent trace. |

**Who decides what.** The LLM only turns the question into `(a, operation, b)`.
Choosing the shortcut is done in Python, so the agent cannot pick a trick that
doesn't apply or invent arithmetic.

## Setup

```bash
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install pip-tools
pip-sync requirements.txt
cp .env.example .env   # then fill in your Azure OpenAI (or OpenAI) settings
```

Change dependencies by editing `requirements.in`, then run `pip-compile --strip-extras requirements.in && pip-sync requirements.txt`.

## Run

```bash
streamlit run app.py
pytest                # offline: uses a fake LLM, no API calls
```

## Adding a shortcut

1. Create `src/quickmath/techniques/<name>.py` with a `@register`ed `Technique` subclass
   (see `add_9.py`): set `name`, `title`, `rule`, `operation`, `priority`, and implement
   `_applies()` and `steps()`.
2. Import it in `src/quickmath/techniques/__init__.py`.
3. Add tests. A Hypothesis test comparing against plain arithmetic catches most mistakes.

The tool specs, agent and UI pick it up automatically.
