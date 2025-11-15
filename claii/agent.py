# claii/agent.py

import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.run_python import schema_run_python_file, run_python_file
from functions.write_file import schema_write_file, write_file


def run_agent(argv: list[str] | None = None, banner_shown: bool = False) -> None:
    if argv is None:
        argv = sys.argv[1:]

    load_dotenv()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # parse prompt + verbose
    if not argv:
        # This is mostly a safety net – normally cli.main handles usage
        print('Usage: claii "<prompt>" [--verbose]')
        sys.exit(1)

    user_prompt = argv[0]
    verbose = len(argv) > 1 and argv[1] == "--verbose"

    if verbose and not banner_shown:
        print(f"User prompt: {user_prompt}")

    # tools
    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )

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
- Explain briefly what you are doing in natural language
"""

    messages: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)])
    ]

    def call_function(function_call_part, verbose: bool = False) -> types.Content:
        function_name = function_call_part.name
        args = dict(function_call_part.args or {})

        # inject working directory
        args.setdefault("working_directory", "calculator")

        if verbose:
            print(f"Calling function: {function_name}({args})")
        else:
            print(f" - Calling function: {function_name}")

        fn_map = {
            "get_files_info": get_files_info,
            "get_file_content": get_file_content,
            "run_python_file": run_python_file,
            "write_file": write_file,
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

    # agent loop
    for _ in range(20):  # max 20 steps
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_prompt,
            ),
        )

        finished_texts: list[str] = []
        any_function_calls = False

        for candidate in response.candidates:
            content = candidate.content
            messages.append(content)  # model's message in conversation

            # inspect for function calls
            for part in content.parts:
                fc = getattr(part, "function_call", None)
                if fc:
                    any_function_calls = True
                    tool_reply = call_function(fc, verbose=verbose)
                    messages.append(tool_reply)
                elif hasattr(part, "text") and part.text:
                    finished_texts.append(part.text)

        if not any_function_calls and finished_texts:
            print("Final response:\n")
            print("\n".join(finished_texts))
            break
    else:
        print("Max agent steps reached without final answer.")
