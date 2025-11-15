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

CLAII (pronounced *“clay”*) is a **command-line–first AI coding agent** that can:

- Inspect and navigate your project files  
- Read file contents  
- Write / overwrite files  
- Execute Python code inside a sandboxed working directory  
- Iterate in an **agent loop** using tool calls (function calling) until a task is done  

It’s designed as a **small, hackable core** that you can extend with more tools, providers, and agent behaviors over time.

---

## ✨ Features (Current)

- 🧠 **Agentic loop**  
  CLAII calls an LLM in a loop, planning tool calls step-by-step until it can give a final answer.

- 📁 **File system tools (scoped)**  
  - `get_files_info` – list files & directories with size and `is_dir`  
  - `get_file_content` – read file contents with length limits  
  - `write_file` – write/overwrite files (within a permitted working dir)  
  - `run_python_file` – execute Python scripts with timeout and output capture  

- 🔐 **Guard-railed workspace**  
  All tools are **restricted to a configured working directory** (e.g. `./calculator`) to avoid the agent wandering across your machine.

- 🧮 **Calculator demo project**  
  A small calculator app (`calculator/`) that CLAII can read, modify, and run—used as a testbed for automated bug fixing and refactoring.

- 🖥️ **CLI entrypoint + ASCII logo**  
  Run `claii "your prompt here"` and get greeted with the CLAII banner before the agent spins up.

---

## 🧭 Roadmap / Planned Features

These are *intended* directions for the extended AgencySwarm/CLAII repo:

- 🔀 **Pluggable AI providers & models**  
  Support multiple backends (e.g. Google Gemini, OpenAI, Anthropic, local LLMs) via a simple config/CLI switch, with a unified tool-calling interface.

- 🧠 **Persistent project memory**  
  Store summaries, decisions, and context per project so CLAII can work on long-running refactors and multi-step bug hunts.

- 🧰 **Extensible tools & MCP integration**  
  Register new tools (e.g. Neo4j MCP servers, HTTP APIs, shell ops) and expose them to agents through a common schema.

- 🕸️ **Multi-agent & parallel workflows**  
  Spin up specialized agents (bug-fixer, refactorer, doc-writer, test-runner) that can coordinate on the same repo or different directories.

- 📚 **Local knowledge-base ingestion & `@mentions`**  
  Let CLAII ingest local docs/specs and reference them via `@architecture.md`, `@api-guides`, `@project_file`, etc.

- 🎨 **Improved CLI UX**  
  Color-coded prompts, tool call traces, diff views, and generally a nicer CLI experience.

---

## 🧱 Architecture Overview

High-level layout (names may vary slightly depending on how you finalize the package):

```text
claii/
  __init__.py
  cli.py          # CLI entrypoint (prints logo, parses args, calls run_agent)
  agent.py        # Core agent loop + function dispatch

functions/
  __init__.py
  get_files_info.py   # get_files_info(...) + schema_get_files_info
  get_file_content.py # get_file_content(...) + schema_get_file_content
  write_file.py       # write_file(...) + schema_write_file
  run_python.py       # run_python_file(...) + schema_run_python_file
  config.py           # e.g. MAX_FILE_CHARS / other function config

calculator/
  main.py         # Calculator CLI app (demo project)
  tests.py        # Unit tests for calculator
  pkg/
    __init__.py
    calculator.py
    render.py

main.py           # Thin wrapper that calls claii.cli:main (for now)
pyproject.toml
README.md
.env.example      # Example environment file (optional)
```

### Agent Loop (Core Idea)

1. **User prompt** – you run:

   ```bash
   claii "fix the precedence bug in calculator"
   ```

2. **System + tools** – the agent sets a system prompt and tells the LLM about available tools (`get_files_info`, `get_file_content`, `run_python_file`, `write_file`).

3. **Tool planning** – the LLM responds with one or more **function calls** (tool invocations) instead of raw text.

4. **Dispatch** – CLAII maps those function calls to Python functions, injects `working_directory="calculator"` and runs them.

5. **Tool responses** – the results are sent back into the conversation as “tool” messages.

6. **Repeat** – the agent calls the LLM again with the updated conversation until:
   - no more tool calls are requested, and  
   - the model returns a final natural language answer.

---

## 📦 Installation

> Assumes Python **3.11+**.

```bash
# Clone your repo
git clone git@github.com:YOUR_ORG/claii.git
cd claii

# Create & activate a virtualenv (recommended)
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate

# Install in editable/dev mode
pip install -e .
```

### Dependencies

Core dependencies (already in `pyproject.toml`):

- `google-genai` – Gemini API client  
- `python-dotenv` – for loading `GEMINI_API_KEY` from `.env`

---

## 🔧 Configuration

Create a `.env` file in the project root with at least:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

For future multi-provider features you might later add:

```env
CLAII_PROVIDER=google       # or "openai", "anthropic", etc. (planned)
CLAII_MODEL=gemini-2.0-flash-001
```

…but right now CLAII defaults to **Gemini** via `google-genai`.

---

## 🚀 Usage

Once installed (and your venv is active):

### 1. Basic invocation

```bash
claii "explain how the calculator works"
```

You should see:

- The **CLAII ASCII logo**  
- Agent logs as it calls tools  
- A final explanation/answer  

### 2. Verbose mode

If you’ve wired `--verbose` through to `run_agent`, you can do:

```bash
claii "list the contents of the pkg directory" --verbose
```

Typical flow:

- It will call `get_files_info({'directory': 'pkg'})`  
- You’ll see the function name + arguments and the tool output  
- The agent may then describe what it found  

### 3. Example prompts

Some fun/diagnostic prompts:

- **List directory contents:**

  ```bash
  claii "what files are in the root of the calculator project?"
  ```

- **Read a file:**

  ```bash
  claii "read the contents of calculator/main.py"
  ```

- **Write a file (within working dir):**

  ```bash
  claii "create a new README snippet in calculator/notes.txt explaining what the calculator does"
  ```

- **Run tests:**

  ```bash
  claii "run the calculator tests"
  ```

- **Fix a bug (the classic demo):**

  ```bash
  claii "fix the bug where '3 + 7 * 2' evaluates to 20 instead of 17 in the calculator"
  ```

---

## 🧩 Tools / Functions

Each tool is:

- **LLM-friendly**: accepts simple strings, returns strings  
- **Guard-railed**: checked against `working_directory`  
- **Schema-declared**: has a `schema_*` `FunctionDeclaration` for the LLM  

### 1. `get_files_info(working_directory, directory=None)`

- Validates the requested path is **inside** `working_directory`  
- Uses `os.listdir`, `os.path.getsize`, `os.path.isdir`  
- Returns lines like:

  ```text
  - main.py: file_size=563 bytes, is_dir=False
  - pkg: file_size=4096 bytes, is_dir=True
  ```

### 2. `get_file_content(working_directory, file_path)`

- Checks the path is inside `working_directory`  
- Reads the file text  
- Truncates if longer than `MAX_FILE_CHARS` (from `functions/config.py`) and appends a truncation notice  
- Returns a string or an `"Error: ..."` message.

### 3. `write_file(working_directory, file_path, content)`

- Ensures the target path is inside `working_directory`  
- Creates parent directories if needed  
- Overwrites/creates the file with `content`  
- Returns:

  ```text
  Successfully wrote to "lorem.txt" (28 characters written)
  ```

### 4. `run_python_file(working_directory, file_path, args=[])`

- Ensures the target is inside `working_directory`  
- Checks the file exists and ends with `.py`  
- Uses `subprocess.run` with:
  - `timeout=30`  
  - `cwd=working_directory`  
  - `capture_output=True`  
- Returns a formatted string:

  ```text
  STDOUT:
  Calculator App
  Usage: python main.py "<expression>"
  Example: python main.py "3 + 5"

  STDERR:
  ... (if any)
  Process exited with code X  # if non-zero
  ```

---

## 🔌 Extensibility Ideas

You can start evolving this into the “AgencySwarm edition” by:

### 1. Multi-provider support

- Create a `claii/llm/` package with:
  - `base.py` – defines a small `LLMBackend` protocol  
  - `google_genai.py` – current implementation  
  - future: `openai_backend.py`, `anthropic_backend.py`, `local_backend.py`  

- Add a `get_backend(provider, model)` function to choose the right backend based on env/CLI args.

### 2. More tools

Examples:

- Git tools (`git diff`, `git status`, `git apply`)  
- Test runners for other languages  
- MCP clients (e.g. Neo4j graph queries, HTTP APIs)  
- Project-level context tools (`summarize_project`, `list_todos`)  

Each tool just needs:

1. A Python implementation  
2. A `schema_*` function declaration  
3. A line in the `FUNCTION_MAP` / tool registry  

### 3. Persistent memory

- Store **per-project** state:
  - Key decisions  
  - File summaries  
  - Known issues / TODOs  

- Could be a simple `.claii` folder in the repo with JSON/YAML that the agent can read via tools.

### 4. Multi-agent workflows

- Define multiple agent “roles” (planner, implementer, reviewer, tester).  
- Orchestrate them from a top-level controller that:
  - Defines tasks  
  - Routes subtasks to different agents  
  - Aggregates results back to the user.  
