# functions/get_files_info.py
import os
from google.genai import types


def get_files_info(working_directory: str, directory: str | None = None) -> str:
    """
    List files in a directory under `working_directory`, returning a human-readable string.

    Always returns a *string* (no exceptions propagate).
    """
    try:
        abs_workdir = os.path.abspath(working_directory)

        # default to working directory itself if directory is None
        if directory is None:
            directory = "."

        abs_target = os.path.abspath(os.path.join(abs_workdir, directory))

        # guard-rail: must stay inside working_directory
        if not abs_target.startswith(abs_workdir):
            return (
                f'Error: Cannot list "{directory}" as it is outside the permitted '
                "working directory"
            )

        if not os.path.isdir(abs_target):
            return f'Error: "{directory}" is not a directory'

        entries = []
        for name in os.listdir(abs_target):
            full_path = os.path.join(abs_target, name)
            try:
                is_dir = os.path.isdir(full_path)
                size = os.path.getsize(full_path)
                entries.append(
                    f"- {name}: file_size={size} bytes, is_dir={is_dir}"
                )
            except OSError as e:
                entries.append(f'- {name}: Error: {e}')

        return "\n".join(entries) if entries else "(empty directory)"

    except Exception as e:  # Catch-all → stringify for the LLM
        return f"Error: {e}"


# ─── Function Declaration Schema for the LLM ─────────────────────────────

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description=(
        "Lists files in the specified directory along with their sizes, "
        "constrained to the working directory."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description=(
                    "The directory to list files from, relative to the working "
                    'directory. Use "." for the root. If not provided, lists '
                    "files in the working directory itself."
                ),
            ),
        },
    ),
)
