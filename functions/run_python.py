# functions/run_python.py
import os
import subprocess
from pathlib import Path


def run_python_file(working_directory: str, file_path: str) -> str:
    """
    Execute a Python file inside `working_directory` with safety guard-rails.

    Returns
    -------
    str
        A formatted result string for the LLM.
    """
    try:
        abs_workdir = Path(working_directory).resolve()
        abs_target = (abs_workdir / file_path).resolve()

        # guard-rails
        if not str(abs_target).startswith(str(abs_workdir)):
            return (
                f'Error: Cannot execute "{file_path}" as it is outside the permitted '
                "working directory"
            )

        if not abs_target.exists():
            return f'Error: File "{file_path}" not found.'

        if abs_target.suffix != ".py":
            return f'Error: "{file_path}" is not a Python file.'

        # run the python file
        proc = subprocess.run(
            ["python3", str(abs_target)],
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
