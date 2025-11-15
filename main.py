# main.py
import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.get_files_info import get_files_info, schema_get_files_info
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.run_python import run_python_file, schema_run_python_file
from functions.write_file import write_file, schema_write_file

# ─── env & client ─────────────────────────────────────────
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ─── function name → callable ────────────────────────────
FUNCTION_MAP = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
}

# ─── tool declarations ───────────────────────────────────
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

# ─── system prompt ───────────────────────────────────────
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, think step-by-step and produce
exactly one function call plan using the names you have been given.

Available operations:
- get_files_info   → List files and directories
- get_file_content → Read file contents
- run_python_file  → Execute Python files with optional arguments
- write_file       → Write or overwrite files

All paths must be relative to the working directory. Do NOT mention or guess
the working directory itself; it will be injected automatically.

Use tools as needed, iteratively, until you can give a clear final answer.
"""


# ─── function dispatcher ─────────────────────────────────
def call_function(function_call_part: types.FunctionCall, verbose: bool = False) -> types.Content:
    """
    Take a FunctionCall from the model, dispatch to the correct Python function,
    and wrap the result as a tool response (types.Content).
    """
    function_name = function_call_part.name
    args = dict(function_call_part.args or {})

    # The model never controls this – we inject it
    args["working_directory"] = "calculator"

    if verbose:
        print(f"Calling function: {function_name}({args})")
    else:
        print(f" - Calling function: {function_name}")

    func = FUNCTION_MAP.get(function_name)

    if func is None:
        # Unknown function name – return a tool-style error object
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    # Actually run the underlying function
    result = func(**args)

    # Wrap as a tool response
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": result},
            )
        ],
    )


# ─── CLI arg handling ────────────────────────────────────
if len(sys.argv) < 2:
    print('Usage: python main.py "<prompt>" [--verbose]')
    sys.exit(1)

user_prompt = sys.argv[1]
verbose = len(sys.argv) > 2 and sys.argv[2] == "--verbose"

# initial conversation
messages: list[types.Content] = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

# ─── Agent loop ──────────────────────────────────────────
MAX_STEPS = 20

for step in range(MAX_STEPS):
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
        ),
    )

    # Add all model messages to the conversation
    any_function_called = False
    for cand in response.candidates:
        messages.append(cand.content)

    # For each candidate, look for function calls and execute them
    for cand in response.candidates:
        content = cand.content
        for part in content.parts:
            fc = getattr(part, "function_call", None)
            if fc:
                any_function_called = True
                tool_msg = call_function(fc, verbose=verbose)

                # Sanity check for function_response structure
                if (
                    not tool_msg.parts
                    or not hasattr(tool_msg.parts[0], "function_response")
                    or tool_msg.parts[0].function_response is None
                ):
                    raise RuntimeError("Function call did not return function_response")

                # If verbose, show the raw function result dict
                if verbose:
                    print(f"-> {tool_msg.parts[0].function_response.response}")

                # Append tool response into the conversation
                messages.append(tool_msg)

    # If the model has no function calls and provided a non-empty text,
    # we consider that the final answer.
    if not any_function_called and response.text and response.text.strip():
        print("Final response:")
        print(response.text.strip())
        break
else:
    # Failsafe: agent spun for MAX_STEPS iterations
    print("Final response:")
    print("(Agent stopped after reaching max iterations.)")
