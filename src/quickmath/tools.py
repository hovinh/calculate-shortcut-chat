"""Tool layer exposed to the LLM agent (OpenAI / Azure OpenAI function-calling format).

The LLM's only job is to translate the user's question into (a, operation, b).
Choosing *which* shortcut to use is done here, deterministically, so the agent
can't pick a trick that doesn't apply.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, ValidationError

from quickmath import registry
from quickmath.models import Operation, Problem


class SolveArgs(BaseModel):
    a: int = Field(description="First operand, exactly as written in the question.")
    operation: Operation = Field(description="Arithmetic operation.")
    b: int = Field(description="Second operand, exactly as written in the question.")
    technique: str | None = Field(
        default=None,
        description="Only set this if the user explicitly asks for a specific shortcut "
        "(use a name from list_shortcuts). Otherwise leave empty and the best one is chosen.",
    )


def solve_with_shortcut(a: int, operation: str, b: int, technique: str | None = None) -> dict[str, Any]:
    problem = Problem(a=a, op=Operation(operation), b=b)
    candidates = registry.find_applicable(problem)
    names = [t.name for t in candidates]
    if technique is not None and technique not in names:
        return {
            "problem": str(problem),
            "found": False,
            "message": f"Shortcut '{technique}' does not apply here.",
            "applicable_shortcuts": names,
        }
    if not candidates:
        return {
            "problem": str(problem),
            "found": False,
            "answer": problem.exact(),
            "message": "No known shortcut applies to this problem.",
        }
    chosen = registry.get(technique) if technique else candidates[0]
    return {
        "found": True,
        "solution": chosen.solve(problem).model_dump(),
        "other_applicable_shortcuts": [t.name for t in candidates if t is not chosen],
    }


def list_shortcuts() -> dict[str, Any]:
    return {
        "shortcuts": [
            {"name": t.name, "title": t.title, "operation": t.operation.value, "rule": t.rule}
            for t in registry.all_techniques()
        ]
    }


def tool_specs() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "solve_with_shortcut",
                "description": "Explain step by step how to compute `a <operation> b` mentally using "
                "the best matching shortcut. Returns verified steps and the answer. "
                "Always call this for a calculation question instead of computing yourself.",
                "parameters": SolveArgs.model_json_schema(),
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_shortcuts",
                "description": "List every mental-math shortcut this assistant knows.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    ]


_DISPATCH = {"solve_with_shortcut": (solve_with_shortcut, SolveArgs), "list_shortcuts": (list_shortcuts, None)}


def dispatch(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Run a tool call from the LLM. Errors are returned (not raised) so the agent can recover."""
    if name not in _DISPATCH:
        return {"error": f"Unknown tool: {name}"}
    func, schema = _DISPATCH[name]
    try:
        if schema is None:
            return func()
        args = schema.model_validate(arguments)
        return func(a=args.a, operation=args.operation.value, b=args.b, technique=args.technique)
    except (ValidationError, ValueError, RuntimeError) as e:
        return {"error": str(e)}
