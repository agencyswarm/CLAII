# claii/agent.py

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List

from google.genai import types

from .providers import get_provider
from .memory import load_memory, save_memory

from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.run_python import schema_run_python_file, run_python_file
from functions.write_file import schema_write_file, write_file
from functions.get_kb_file import schema_get_kb_file, get_kb_file


# ─── Agent config ──────────────────────────────────────────────────────────────

MAX_AGENT_STEPS = 20          # max reasoning/tool-use iterations per run
MAX_MEMORY_MESSAGES = 200     # how many messages to keep when pruning history
DEFAULT_WORKING_DIR = "calculator"


# ─── Arg parsing & helpers ─────────────────────────────────────────────────────

def _parse_args(argv: List[str]) -> tuple[str, bool, bool, bool]:
    """
    Parse CLI args for the agent.

    Expected:
        claii "<prompt>" [--verbose] [--no-memory] [--no-prune]

    Returns:
        (user_prompt, verbose, use_memory, prune_history)
    """
    if not argv:
        print('Usage: claii "<prompt>" [--verbose] [--no-memory] [--no-prune]')
        sys.exit(1)

    user_prompt = argv[0]
    flags = argv[1:]

    verbose = "--verbose" in flags
    use_memory = "--no-memory" not in flags
    prune_history = "--no-prune" not in flags

    return user_prompt, verbose, use_memory, prune_history


def _prune_messages(
    messages: List[types.Content],
    max_messages: int = MAX_MEMORY_MESSAGES,
) -> List[types.Content]:
    """
    Keep only the most recent `max_messages` entries in the history.
    System prompt is separate, so this only affects conversation messages.
    """
    if len(messages) <= max_messages:
        return messages
    return messages[-max_messages:]


def _build_tools() -> types.Tool:
    """Return the Tool spec with all function declarations."""
    return types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
            schema_get_kb_file,
        ]
    )


# ─── @-mention expansion ───────────────────────────────────────────────────────

KB_PATTERN = re.compile(r"@kb/([^\s]+)")
FILE_PATTERN = re.compile(r"@file:([^\s]+)")


def expand_at_mentions(prompt: str, working_directory: str) -> str:
    """
    Expand @kb/file.md into inline KB content, and annotate @file:path/to/file.py
    so the agent is nudged to call the right tools.

    - @kb/foo.md → embeds the content of kb/foo.md (using get_kb_file)
    - @file:src/main.py → leaves a descriptive hint telling the model to use
      get_file_content with file_path="src/main.py"
    """
    text = prompt

    # 1) Inline KB content for @kb/...
    def kb_repl(match: re.Match) -> str:
        kb_rel = match.group(1)  # e.g. "design.md"
        kb_content = get_kb_file(working_directory, kb_rel)

        if isinstance(kb_content, str) and kb_content.startswith("Error:"):
            # Keep the mention but annotate the error for transparency
            return f'@kb/{kb_rel} (KB load error: {kb_content})'

        return (
            f'Below is the content of knowledge base file "kb/{kb_rel}":\n'
            f"--- KB START [{kb_rel}] ---\n"
            f"{kb_content}\n"
            f"--- KB END [{kb_rel}] ---\n"
        )

    text = KB_PATTERN.sub(kb_repl, text)

    # 2) Annotate explicit @file paths – do NOT auto-load, just hint
    def file_repl(match: re.Match) -> str:
        path = match.group(1)  # e.g. "calculator/pkg/calculator.py"
        return (
            f'"{path}" (project file reference; '
            f'use get_file_content with file_path="{path}")'
        )

    text = FILE_PATTERN.sub(file_repl, text)

    return text


# ─── Function dispatcher ───────────────────────────────────────────────────────

def _call_function(function_call_part, verbose: bool = False) -> types.Content:
    """
    Dispatch a model function_call to the underlying Python implementation
    and wrap the result back into a tool response Content.
    """
    function_name = function_call_part.name
    args = dict(function_call_part.args or {})

    # Inject working directory – model never controls this.
    args.setdefault("working_directory", DEFAULT_WORKING_DIR)

    if verbose:
        print(f"Calling function: {function_name}({args})")
    else:
        print(f" - Calling function: {function_name}")

    fn_map = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "run_python_file": run_python_file,
        "write_file": write_file,
        "get_kb_file": get_kb_file,
    }

    fn = fn_map.get(function_name)
    if fn is None:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    result = fn(**args)

    if verbose:
        print(f"-> {result!r}")

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": result},
            )
        ],
    )


# ─── Main agent entrypoint ─────────────────────────────────────────────────────

def run_agent(argv: List[str] | None = None, banner_shown: bool = False) -> None:
    """
    Core agent loop. This is called from claii.cli.main().
    """
    if argv is None:
        argv = sys.argv[1:]

    user_prompt, verbose, use_memory, prune_history = _parse_args(argv)

    if verbose and not banner_shown:
        print(f"User prompt: {user_prompt}")

    provider = get_provider()
    tools = _build_tools()
    project_root = Path.cwd()
    working_directory = DEFAULT_WORKING_DIR

    system_prompt = """
You are CLAII, a helpful AI coding agent that edits and runs code in the user's workspace.

You can:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

You must ALWAYS:
- Keep paths relative to the working directory
- Use tools instead of guessing file contents
- Make a plan before making changes
- Validate your changes by running tests when available

Refactor / bugfix workflow:

1. Use get_files_info to discover relevant files.
2. Use get_file_content to inspect code.
3. Describe your plan briefly in natural language.
4. Use write_file to apply small, focused changes.
5. Use run_python_file to run tests or scripts to verify.

Knowledge base usage:

- When the user mentions @kb/<path>, treat it as a reference to the file "kb/<path>"
  under the working directory. Inline KB content or call get_kb_file as needed.
- When the user mentions @file:<path>, treat it as a hint to inspect that project file
  via get_file_content with file_path="<path>".
"""

    # ── Memory bootstrap ───────────────────────────────────────────────────────
    if use_memory:
        messages: List[types.Content] = load_memory(project_root)
    else:
        messages = []

    # Preprocess @-mentions and append the new user request
    expanded_prompt = expand_at_mentions(user_prompt, working_directory=working_directory)
    messages.append(
        types.Content(role="user", parts=[types.Part(text=expanded_prompt)])
    )

    # ── Agent loop ────────────────────────────────────────────────────────────
    for _ in range(MAX_AGENT_STEPS):
        response = provider.generate(
            messages=messages,
            tools=[tools],
            system_prompt=system_prompt,
        )

        finished_texts: list[str] = []
        any_function_calls = False

        for candidate in response.candidates:
            content = candidate.content
            # Model's reply goes into the conversation
            messages.append(content)

            # Inspect for function calls
            for part in content.parts:
                fc = getattr(part, "function_call", None)
                if fc:
                    any_function_calls = True
                    tool_reply = _call_function(fc, verbose=verbose)
                    messages.append(tool_reply)
                elif hasattr(part, "text") and part.text:
                    finished_texts.append(part.text)

        # No more tool calls + some final text → we're done
        if not any_function_calls and finished_texts:
            final = "\n".join(finished_texts).strip()
            if final:
                print("Final response:\n")
                print(final)
            break
    else:
        # Failsafe if no final answer after MAX_AGENT_STEPS
        print("Max agent steps reached without final answer.")

    # ── Persist memory ────────────────────────────────────────────────────────
    if use_memory:
        if prune_history:
            messages = _prune_messages(messages, MAX_MEMORY_MESSAGES)
        save_memory(project_root, messages)
