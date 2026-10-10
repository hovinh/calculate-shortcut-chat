from __future__ import annotations

from quickmath.models import Problem
from quickmath.base import Technique

_REGISTRY: dict[str, Technique] = {}


def register(cls: type[Technique]) -> type[Technique]:
    if cls.name in _REGISTRY:
        raise ValueError(f"Duplicate technique name: {cls.name}")
    _REGISTRY[cls.name] = cls()
    return cls


def get(name: str) -> Technique:
    _load()
    return _REGISTRY[name]


def all_techniques() -> list[Technique]:
    _load()
    return list(_REGISTRY.values())


def find_applicable(problem: Problem) -> list[Technique]:
    """Techniques that apply to `problem`, best first."""
    return sorted(
        (t for t in all_techniques() if t.applies(problem)),
        key=lambda t: t.priority,
        reverse=True,
    )


def _load() -> None:
    # Importing the package runs every @register decorator.
    import quickmath.techniques  # noqa: F401
