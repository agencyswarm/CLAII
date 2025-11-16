# functions/get_kb_file.py
import os
from pathlib import Path
from google.genai import types


def get_kb_file(working_directory: str, kb_path: str) -> str:
    """
    Read a file from the knowledge base directory inside working_directory/kb.
    """
    try:
        workdir = Path(working_directory).resolve()
        kb_root = (workdir / "kb").resolve()
        target = (kb_root / kb_path).resolve()

        if not str(target).startswith(str(kb_root)):
            return f'Error: Cannot read "{kb_path}" as it is outside the KB directory'

        if not target.exists() or not target.is_file():
            return f'Error: KB file not found: "{kb_path}"'

        text = target.read_text(encoding="utf-8")
        # optionally truncate to avoid token blowup
        return text[:10000]
    except Exception as e:
        return f"Error: {e}"

schema_get_kb_file = types.FunctionDeclaration(
    name="get_kb_file",
    description="Reads a knowledge base file under the kb/ directory for additional context.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "kb_path": types.Schema(
                type=types.Type.STRING,
                description="Path under kb/, e.g. 'design.md' or 'lang/agent-architecture.md'",
            ),
        },
        required=["kb_path"],
    ),
)