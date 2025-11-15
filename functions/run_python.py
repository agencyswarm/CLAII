# functions/run_python.py
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Sequence

from google.genai import types


def run_python_file(
    working_directory: str,
    file_path: str,
    args: Sequence[str] | None = None,
) -> str:
    """
    Execute a Python file inside `working_directory` with safety guard-rails.

    Always returns a string formatted for the LLM:
    - Includes STDOUT / STDERR
    - Notes non-zero exit codes
    - Handles timeouts and unexpected exceptions
    """
    try:
        abs_workdir = Path(working_directory).resolve()
        abs_target = (abs_workdir / file_path).resolve()

        # guard-rails: keep execution inside working_directory
        if not str(abs_target).startswith(str(abs_workdir)):
            return (
                f'Error: Cannot execute "{file_path}" as it is outside the permitted '
                "working directory"
            )

        if not abs_target.exists():
            return f'Error: File "{file_path}" not found.'

        if abs_target.suffix != ".py":
            return f'Error: "{file_path}" is not a Python file.'

        # build command: python file [args...]
        cmd = ["python3", str(abs_target)]
        if args:
            cmd.extend(args)

        proc = subprocess.run(
            cmd,
            cwd=abs_workdir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()

        parts: list[str] = []
        if stdout:
            parts.append(f"STDOUT:\n{stdout}")
        if stderr:
            parts.append(f"STDERR:\n{stderr}")
        if proc.returncode != 0:
            parts.append(f"Process exited with code {proc.returncode}")

        return "\n".join(parts) if parts else "No output produced."

    except subprocess.TimeoutExpired:
        return "Error: executing Python file: timed out after 30 seconds"
    except Exception as e:  # noqa: BLE001
        return f"Error: executing Python file: {e}"


# Tool / function declaration for the LLM
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description=(
        "Executes a Python file inside the working directory and returns its "
        "stdout/stderr and exit code information."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description=(
                    "Path to the Python file to execute, relative to the working "
                    "directory (e.g. 'main.py' or 'tests.py')."
                ),
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description=(
                    "Optional list of additional command-line arguments to pass to "
                    "the Python script."
                ),
                items=types.Schema(type=types.Type.STRING),
            ),
        },
    ),
)
