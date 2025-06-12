# functions/get_files_info.py
import os


def get_files_info(working_directory: str, directory: str | None = None) -> str:
    """
    Build a human-readable listing of a directory.

    Parameters
    ----------
    working_directory : str
        The root directory the agent is allowed to touch.
    directory : str | None
        The directory to list, relative to `working_directory`.
        If None or ".", the working_directory itself is listed.

    Returns
    -------
    str
        Either a multi-line listing or an error message that
        always starts with 'Error:' so the LLM can parse it.
    """

    # 1️⃣ Resolve absolute paths
    abs_workdir = os.path.abspath(working_directory)
    target = abs_workdir if directory in (None, ".", "") else os.path.abspath(
        os.path.join(abs_workdir, directory)
    )

    # 2️⃣ Guard-rails
    if not target.startswith(abs_workdir):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    if not os.path.isdir(target):
        return f'Error: "{directory}" is not a directory'

    # 3️⃣ Build the listing
    lines: list[str] = []
    try:
        for entry in sorted(os.listdir(target)):
            full = os.path.join(target, entry)
            size = os.path.getsize(full)
            is_dir = os.path.isdir(full)
            lines.append(f"- {entry}: file_size={size} bytes, is_dir={is_dir}")
    except Exception as e:  # catch *any* OS error and stringify
        return f"Error: {e}"

    return "\n".join(lines) if lines else "(empty directory)"
