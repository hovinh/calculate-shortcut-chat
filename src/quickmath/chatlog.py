"""Save each chat session to a JSON file, so feedback can point at an exact conversation.

One file per session, rewritten after every change. Each turn keeps the question, the
tool calls with their results, the answer (or error), and any 👍/👎 feedback with a note.
The code version is recorded too, since prompts and shortcuts change over time.
"""

from __future__ import annotations

import json
import secrets
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True, cwd=Path(__file__).parent, timeout=5
    ).stdout.strip()


def _code_version() -> str | None:
    """Short git commit, with "+dirty" if there are uncommitted changes; None outside git."""
    try:
        return _git("rev-parse", "--short", "HEAD") + ("+dirty" if _git("status", "--porcelain") else "")
    except (OSError, subprocess.SubprocessError):
        return None


class ChatLog:
    def __init__(self, directory: Path, model: str):
        now = datetime.now()
        self.path = Path(directory) / f"{now:%Y%m%d-%H%M%S}-{secrets.token_hex(3)}.json"
        self.data: dict[str, Any] = {
            "started_at": now.isoformat(timespec="seconds"),
            "model": model,
            "code_version": _code_version(),
            "turns": [],
        }

    def add_turn(
        self, question: str, tool_calls: list[dict[str, Any]], answer: str | None = None, error: str | None = None
    ) -> int:
        """Record a finished turn and return its number (1, 2, ...)."""
        number = len(self.data["turns"]) + 1
        self.data["turns"].append(
            {
                "turn": number,
                "at": datetime.now().isoformat(timespec="seconds"),
                "question": question,
                "tool_calls": tool_calls,
                "answer": answer,
                "error": error,
                "feedback": None,
            }
        )
        self._save()
        return number

    def set_feedback(self, turn: int, rating: str | None, note: str = "") -> None:
        """rating is "up", "down" or None (cleared); an empty note with no rating clears the feedback."""
        note = note.strip()
        self.data["turns"][turn - 1]["feedback"] = {"rating": rating, "note": note} if rating or note else None
        self._save()

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
