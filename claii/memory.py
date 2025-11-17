# claii/memory.py
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, List
from google.genai import types

MEMORY_FILE = ".claii_memory.json"

def _memory_path(project_root: Path) -> Path:
    return project_root / MEMORY_FILE

def load_memory(project_root: str | Path) -> List[types.Content]:
    path = _memory_path(Path(project_root))
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

    messages: List[types.Content] = []
    for item in data:
        role = item.get("role", "user")
        text = item.get("text", "")

        # 🔧 Normalize roles for Gemini: only "user" or "model" allowed
        if role not in ("user", "model"):
            role = "user"

        messages.append(
            types.Content(
                role=role,
                parts=[types.Part(text=text)],
            )
        )
    return messages


def save_memory(project_root: str | Path, messages: List[types.Content]) -> None:
    path = _memory_path(Path(project_root))
    serializable: list[dict[str, Any]] = []
    for m in messages:
        text_parts = [p.text for p in m.parts if hasattr(p, "text") and p.text]
        serializable.append(
            {"role": m.role, "text": "\n".join(text_parts)}
        )
    path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
