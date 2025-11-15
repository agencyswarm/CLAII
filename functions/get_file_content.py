# functions/get_file_content.py
import os
from google.genai import types
from .config import MAX_FILE_CHARS  # you already have this from earlier step


def get_file_content(working_directory: str, file_path: str) -> str:
    """
    Return the text of a file inside the working directory, with guard-rails.
    Always returns a string (no exceptions propagate).
    """
    try:
        abs_workdir = os.path.abspath(working_directory)
        abs_target = os.path.abspath(os.path.join(abs_workdir, file_path))

        if not abs_target.startswith(abs_workdir):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(abs_target):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(abs_target, "r", encoding="utf-8") as f:
            content = f.read(MAX_FILE_CHARS + 1)

        # Truncate if too long
        if len(content) > MAX_FILE_CHARS:
            content = (
                content[:MAX_FILE_CHARS]
                + f'\n[...File "{file_path}" truncated at {MAX_FILE_CHARS} characters]'
            )

        return content

    except Exception as e:
        return f"Error: {e}"


# --- Function declaration schema for the LLM ---
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read the contents of a file within the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file, relative to the working directory.",
            ),
        },
        required=["file_path"],
    ),
)
