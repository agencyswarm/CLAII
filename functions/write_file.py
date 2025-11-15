# functions/write_file.py
from __future__ import annotations

from pathlib import Path
from google.genai import types


def write_file(working_directory: str, file_path: str, content: str) -> str:
    """
    Write or overwrite a text file inside `working_directory` with guard-rails.

    Always returns a string describing success or error.
    """
    try:
        abs_workdir = Path(working_directory).resolve()
        abs_target = (abs_workdir / file_path).resolve()

        # guard-rails: keep writes inside working_directory
        if not str(abs_target).startswith(str(abs_workdir)):
            return (
                f'Error: Cannot write to "{file_path}" as it is outside the permitted '
                "working directory"
            )

        # ensure parent directory exists if needed
        parent = abs_target.parent
        if not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)

        # overwrite file contents
        text = str(content)
        with abs_target.open("w", encoding="utf-8") as f:
            f.write(text)

        return f'Successfully wrote to "{file_path}" ({len(text)} characters written)'

    except Exception as e:  # noqa: BLE001
        return f"Error: {e}"


# Tool / function declaration for the LLM
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes or overwrites a text file in the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description=(
                    "Relative path of the file to write. "
                    "Examples: 'main.txt', 'pkg/morelorem.txt'."
                ),
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The text content to write into the file.",
            ),
        },
    ),
)
