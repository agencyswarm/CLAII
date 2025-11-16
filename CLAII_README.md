```text
   ██████╗ ██╗      █████╗ ██╗██╗
  ██╔════╝ ██║     ██╔══██╗██║██║
  ██║      ██║     ███████║██║██║
  ██║      ██║     ██╔══██║██║██║
  ╚██████╗ ███████╗██║  ██║██║██║
   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝╚═╝   
   (CLAII)
```

# CLAII – CLI-First AI Coding Agent

CLAII (pronounced “clay”) is a **command-line–first AI coding agent** that can:

- Inspect and navigate your project files  
- Read file contents  
- Write / overwrite files  
- Execute Python code inside a sandboxed working directory  
- Iterate in an agent loop using tool calls (function calling) until a task is done  
- Use a local knowledge base and lightweight memory to stay context-aware  

It’s designed as a small, hackable core that you can extend with more tools, providers, and agent behaviors over time.

---

## ✨ Features (Current)

### 🧠 Agentic loop

CLAII calls an LLM in a loop, planning tool calls step-by-step until it can give a final answer or finishes a sequence of edits/tests.

### 📁 File system tools (scoped)

- `get_files_info` – list files & directories with size and `is_dir`  
- `get_file_content` – read file contents with a max-length guard (`MAX_FILE_CHARS`)  
- `write_file` – write/overwrite files (within a permitted working dir)  
- `run_python_file` – execute Python scripts with timeout and output capture  

### 🔐 Guard-railed workspace

All tools are restricted to a configured working directory (by default `./calculator`) to avoid the agent wandering across your machine.

### 📚 Knowledge base integration + @ mentions

- `kb/` folder under the working directory  
- `@kb/<path>` – inline knowledge-base content directly into the prompt  
- `@file:<path>` – hint CLAII to inspect a specific project file via `get_file_content`  

### 🧠 Lightweight, optional memory

- Stores a compressed conversation history in `.claii_memory.json` per project  
- Can be disabled with `--no-memory`  
- History pruning can be toggled via `--no-prune`  

### 🧮 Calculator demo project

A small calculator app (`calculator/`) that CLAII can read, modify, and run—used as a testbed for automated bug fixing and refactoring.

### 🖥️ CLI entrypoint + ASCII logo

Run `claii "your prompt here"` and get greeted with the CLAII banner before the agent spins up.

---

## 🧭 Roadmap / Planned Features

Intended directions for the extended AgencySwarm / CLAII version:

### 🔀 Pluggable AI providers & models

Support multiple backends (e.g. Google Gemini, OpenAI, Anthropic, local LLMs) via a simple config/CLI switch, with a unified tool-calling interface exposed to the agent.

### 🧠 Richer project memory

- Store summaries, decisions, and architectural notes per project  
- Offer commands to inspect/prune/clear memory explicitly  

### 🧰 Extensible tools & MCP integration

- Register new tools (e.g. Neo4j via MCP, HTTP APIs, git operations)  
- Auto-register them via a simple `functions/` convention and schema declarations  

### 🕸️ Multi-Agent Swarms & parallel workflows

- Specialized agents: bug-fixer, refactorer, doc-writer, test-runner, etc.  
- Parallel operations on different files/directories with a coordination layer  

### 📚 Deeper knowledge-base workflows

- KB-aware planning (“read design docs first, then refactor”)  
- Structured KB summaries and embedding-based retrieval  

### 🎨 Improved CLI UX

- Color-coded input/output and tool traces  
- Optional diff previews when files are modified  
- “Quiet” and “debug” modes for different levels of verbosity  

---

## 🧱 Architecture Overview

Current high-level layout:

```text
claii/
  __init__.py
  cli.py          # CLI entrypoint (prints logo, parses args, calls run_agent)
  agent.py        # Core agent loop + function dispatch + memory + @mentions
  memory.py       # Load/save compressed conversation history
  config.py       # Provider config (CLAII_PROVIDER, CLAII_MODEL)
  providers.py    # GeminiProvider and future multi-provider abstractions

functions/
  __init__.py
  config.py             # e.g. MAX_FILE_CHARS / function-level config
  get_files_info.py     # get_files_info(...) + schema_get_files_info
  get_file_content.py   # get_file_content(...) + schema_get_file_content
  write_file.py         # write_file(...) + schema_write_file
  run_python.py         # run_python_file(...) + schema_run_python_file
  get_kb_file.py        # get_kb_file(...) + schema_get_kb_file

calculator/
  __init__.py
  main.py         # Calculator CLI app (demo project)
  tests.py        # Unit tests for calculator
  main.txt        # Example text file
  README.md
  pkg/
    __init__.py
    calculator.py
    render.py
    morelorem.txt

pyproject.toml
README.md
.env.example        # Example environment file (optional)
.claii_memory.json  # Created at runtime (per-project memory)
```

---

## 🧠 Agent Behavior & System Prompt

At a high level, the agent is instructed along these lines:

### Capabilities

- List files and directories  
- Read file contents  
- Execute Python files with optional arguments  
- Write or overwrite files  

### Must always

- Keep paths relative to the working directory  
- Use tools instead of guessing file contents  
- Make a plan before making changes  
- Validate changes by running tests when available  

### Refactor / bugfix workflow

1. Use `get_files_info` to discover relevant files  
2. Use `get_file_content` to inspect code  
3. Describe a brief plan in natural language  
4. Use `write_file` to apply focused changes  
5. Use `run_python_file` to run tests or scripts to verify  

### Knowledge-base usage

- `@kb/<path>` → treated as a reference to `kb/<path>` under the working directory  
- `@file:<path>` → treated as a hint to inspect that project file via `get_file_content`  

The agent loop keeps calling the provider’s `generate(...)` method until:

- There are no more tool calls requested, and  
- The model returns non-empty final text.

---

## 📦 Installation

Requires **Python 3.11+**.

```bash
# Clone the repo
git clone git@github.com:agencyswarm/CLAII.git
cd CLAII

# Create & activate a virtualenv (recommended)
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scriptsctivate

# Install in editable/dev mode
pip install -e .

# Run once to verify the CLI is installed
claii --help  # (future: help text; for now, just try a prompt)
```

### Dependencies

Core dependencies (declared in `pyproject.toml`):

- `google-genai` – Gemini API client  
- `python-dotenv` – load `GEMINI_API_KEY` and other env vars  

---

## 🔧 Configuration

Create a `.env` file in the project root with at least:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

Current provider abstraction lives in `claii/providers.py`:

- `GeminiProvider` wraps `google-genai` and handles:
  - API key loading (`dotenv`)  
  - Model selection (`gemini-2.0-flash-001` by default)  

Optional future configuration (already scaffolded via `claii/config.py`):

```bash
CLAII_PROVIDER=google-genai
CLAII_MODEL=gemini-2.0-flash-001
```

At the moment, `get_provider()` simply returns a `GeminiProvider`, but the config class is in place to add more providers later.

---

## 🚀 Usage

Once installed (and your venv is active):

### 1. Basic invocation

```bash
claii "explain how the calculator works"
```

You should see:

- The CLAII ASCII logo  
- Tool call lines (e.g. `Calling function: get_files_info({...})`)  
- A final explanation  

### 2. Flags

The current CLI is wired like this:

```bash
claii "<prompt>" [--verbose] [--no-memory] [--no-prune]
```

- `--verbose`  
  Prints tool call arguments and raw tool results (useful for debugging).

- `--no-memory`  
  Disables loading/saving `.claii_memory.json` for the current project.  
  The agent works just on the current prompt + steps in this run.

- `--no-prune`  
  Disables pruning of message history before saving.  
  By default, only the last `MAX_MEMORY_MESSAGES` (e.g. 200) are kept.

#### Examples

```bash
# Normal run, memory enabled and pruned
claii "fix the bug where 3 + 7 * 2 returns 20 instead of 17"

# Debug everything, but do not persist history
claii "run the calculator tests" --verbose --no-memory

# Long-running debugging session, keep full history
claii "help me refactor calculator/pkg/calculator.py" --no-prune
```

### 3. Knowledge base & @ mentions

Under the working directory (default `calculator/`), you can create:

```text
calculator/
  kb/
    design.md
    architecture/decisions.md
    lang/agent-architecture.md
```

Use them in prompts like:

```bash
# Inline KB context from kb/design.md
claii "Using @kb/design.md, refactor the calculator to follow the design guidelines."

# Hint to a specific project file
claii "Based on @kb/lang/agent-architecture.md, review @file:calculator/pkg/calculator.py and suggest improvements."
```

#### Behavior

- `@kb/<path>`  
  - Matches `KB_PATTERN = r"@kb/([^\s]+)"`  
  - CLAII expands it into inline text:

    ```text
    Below is the content of knowledge base file "kb/<path>":
    --- KB START [<path>] ---
    ... file contents (truncated if very long) ...
    --- KB END [<path>] ---
    ```

- `@file:<path>`  
  - Matches `FILE_PATTERN = r"@file:([^\s]+)"`  
  - CLAII does not auto-load the file, but rewrites it as a hint:

    ```text
    "<path>" (project file reference; use get_file_content with file_path="<path>")
    ```

Other uses of `@` (emails, social handles, normal text) are not touched, because only these specific patterns are recognized.

### 4. Example prompts

List directory contents:

```bash
claii "what files are in the root of the calculator project?" --verbose
```

Read a file:

```bash
claii "read the contents of calculator/main.py"
```

Write a file (within working dir):

```bash
claii "create a new file calculator/notes.txt summarising what the calculator does"
```

Run tests:

```bash
claii "run the calculator tests in calculator/tests.py"
```

Classic bugfix demo:

```bash
claii "fix the bug where '3 + 7 * 2' evaluates to 20 instead of 17 in the calculator"
```

---

## 🧠 Memory Model

Memory is implemented in `claii/memory.py` as a simple JSON log:

- File: `.claii_memory.json` in the project root  
- Schema: list of `{ "role": "...", "text": "..." }` records  
- Only role and concatenated text parts are persisted to keep it compact  

On startup:

If memory is enabled (default), CLAII calls:

```python
messages = load_memory(project_root)
```

Then it appends the current (possibly expanded) user prompt:

```python
messages.append(
    types.Content(role="user", parts=[types.Part(text=expanded_prompt)])
)
```

On shutdown:

If memory is enabled, it optionally prunes the messages via `_prune_messages` and then:

```python
save_memory(project_root, messages)
```

You can always disable memory for a run with `--no-memory`, or prevent pruning with `--no-prune`.

---

## 🔌 Providers

Provider abstraction lives in `claii/providers.py`:

```python
class GeminiProvider:
    def __init__(self, model_name: str = "gemini-2.0-flash-001") -> None:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        ...
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate(self, *, messages, tools, system_prompt):
        return self.client.models.generate_content(
            model=self.model_name,
            contents=messages,
            config=types.GenerateContentConfig(
                tools=tools,
                system_instruction=system_prompt,
            ),
        )
```

The agent only calls:

```python
provider = get_provider()
response = provider.generate(
    messages=messages,
    tools=[tools],
    system_prompt=system_prompt,
)
```

Future additions:

- `OpenAIProvider`  
- `AnthropicProvider`  
- `LocalProvider` (e.g. vLLM, LM Studio, etc.)  

Each just needs to implement the same `generate(...)` signature.

---

## 🧩 Extending CLAII

Some directions you can take this project:

### 1. More tools

Add modules under `functions/` and register them in `agent.py`:

- `functions/git_tools.py`  
- `functions/http_request.py`  
- `functions/test_runner.py`  

Each should export:

- `your_tool(...)` – pure Python string-in/string-out  
- `schema_your_tool` – `types.FunctionDeclaration` describing its parameters  

Then include them in:

- `_build_tools()` – add to `function_declarations=[...]`  
- `_call_function()` – extend `fn_map = { ... }`  

### 2. Multi-agent orchestration

Build a higher-level controller that:

- Spawns multiple `run_agent` calls with different system prompts/roles  
- Shares a common memory file or passes summaries between agents  

Orchestration ideas:

- Planner → Implementer → Tester → Reviewer  
- Long-running refactor pipelines  

### 3. Better UX

- Color output using `rich` or `colorama`  
- Add a `--diff` flag that prints a minimal diff when `write_file` changes a file  
- Add `--plan-only` mode where the agent only inspects and proposes a plan without writing files  

---

## 📝 License

Copyright (C) Swarmic LLC. All Rights Reserved.
