---
name: auto-orchestrator
description: >-
  Autonomous task decomposition, code-first deterministic offloading, universal command timeout watchdog,
  and multi-agent orchestrator. Automatically offloads computational, parsing, and data tasks to deterministic scripts,
  enforces execution timeouts, splits prompts into subagents, and routes tasks through a hierarchical model selector
  (Priority 1: Free models like Groq, Nemotron, Cohere; Priority 2: GPT/Claude; Priority 3: Lightweight Gemini like flash_lite/flash),
  minimizing token consumption and accelerating responses.
---

# Auto-Orchestrator Skill

This skill governs the autonomous division of labor across deterministic script execution, subagents, and free external models to eliminate token anxiety, maximize speed, and prevent LLM context bloat.

## Architecture

```
User Prompt / Task
        │
        ▼
[Task Classifier & Decomposer]
        │
        ├───────────────────────────────────────────────────────┐
        ▼                                                       ▼
[Algorithmic / Data / Parsing Tasks]           [Generative / Architecture Tasks]
        │                                                       │
  Code-First Deterministic Offloading               Multi-Agent Subagent Cascade
        │                                                       │
  • Write disposable Python/Bash script              • Subagent (Model: flash_lite)
  • Execute with Timeout Guard (0 tokens)            • router.py (Cohere / Groq / Nemotron)
  • Return compact summary/JSON                      • Zero-token external inference
        │                                                       │
        └───────────────────────┬───────────────────────────────┘
                                │
                                ▼
               [Main Agent: Synthesizer & Coordinator]
                                │
                                ▼
               Final Clean Response to User (Persian RTL)
```

---

## ⚡ Code-First Offloading & Computational Scripting

> **Core Philosophy**: Never let an LLM do what 5 lines of Python or Bash can calculate deterministically in 10ms with zero token cost.

### When to Offload Deterministically:

1. **Large File Search & Log Inspection**: Searching through megabytes of logs, text files, or source trees.
2. **Data Parsing & Transformation**: Extracting specific keys or filtering massive JSON, YAML, CSV, or XML documents.
3. **Counting, Math & Statistics**: Line counts, frequency distributions, token estimations, arithmetic, or financial formulas.
4. **Codebase & Directory Auditing**: Analyzing import graphs, dead code, file sizes, or AST trees.
5. **Web Scraping & DOM Extraction**: Extracting specific clean fields or tables rather than dumping full HTML pages into context.

---

### Execution Patterns & Concrete Workflows

#### Pattern 1: Inline Disposable One-Liners (`python3 -c` / `jq` / `awk`)
Use for immediate calculations, aggregations, or key extractions without cluttering disk or context.

```bash
# Example: Count occurrences of specific error codes in a 50MB log file
python3 -c "
import collections, re
with open('app.log') as f:
    counts = collections.Counter(re.findall(r'HTTP 5\d\d', f.read()))
print(dict(counts))
"
```
*Result in context*: `{'HTTP 500': 142, 'HTTP 502': 12, 'HTTP 504': 3}` instead of 500,000 tokens of raw log text!

#### Pattern 2: Scratchpad Extraction Script
For multi-step file manipulation, AST inspection, or bulk transformations, write a temporary script under `/tmp` or scratchpad:

```python
# /tmp/filter_schema.py
import json

with open("massive_schema.json", "r") as f:
    data = json.load(f)

# Extract only relevant endpoint paths and response schemas
compact = {
    path: list(methods.keys())
    for path, methods in data.get("paths", {}).items()
    if "/api/v2" in path
}

with open("/tmp/schema_summary.json", "w") as f:
    json.dump(compact, f, indent=2)

print(f"Extracted {len(compact)} endpoints.")
```

Run via terminal, then read only `/tmp/schema_summary.json`.

#### Pattern 3: Bulk File Refactoring & AST Analysis
Instead of opening dozens of files via agent tools, use Python's `ast` or regex to parse and transform:

```bash
# Example: Find all circular imports or missing type annotations across 100 modules
python3 -c "
import ast, glob

for file in glob.glob('src/**/*.py', recursive=True):
    with open(file) as f:
        tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.returns is None:
                print(f'{file}:{node.name} missing return type')
"
```

---

## 🛡️ Universal Command Timeout & Execution Watchdog Pattern

All terminal executions (`run_command`), background scripts, and deterministic offloading tasks MUST be guarded against indefinite hangs, deadlocks, and silent stalls.

### 1. Defensive Timeout Guarding

Always wrap shell commands with a defensive execution timeout:

```bash
# Standard command with 30s timeout guard
timeout 30s <command>

# Subshell or complex pipeline with graceful fallback and SIGKILL
timeout --kill-after=5s 60s <command>
```

- **Default Timeout**: 30s to 60s for standard scripts, tests, data filtering, and queries.
- **Heavy Operations**: Adjust to task-appropriate limits (e.g. 120s–300s) for dependency installations (`pip`, `npm`), Docker builds, or large file downloads.
- **Synchronous Commands**: Set `WaitMsBeforeAsync` appropriately (e.g. 5000ms–10000ms) to detect fast completion without unnecessary backgrounding.

---

### 2. Detection & Status Diagnosis

When a command terminates:
1. **Exit Code 124**: Indicates that GNU `timeout` terminated the process because the time limit expired.
2. **Background Tasks (`manage_task`)**: If a background task runs past its expected duration without output or heartbeat, check its status and log output via `manage_task(Action='status')`.
3. **Analyze Root Cause**:
   - Was the process waiting for interactive user input (`stdin`, unbuffered prompt)?
   - Was there a network bottleneck (stalled download or API call)?
   - Was it an infinite loop or deadlock in a script?
   - Was it simply a resource-intensive workload needing more time?

---

### 3. Intelligent User Reporting & Interactive Timeout Adjustment

When a command times out or hangs:
- **NEVER** silently hang, retry in a blind loop, or throw a generic error.
- Proactively report the exact situation in Persian RTL:
  1. Specify the exact command and how long it ran before timing out.
  2. Explain the suspected cause (network, heavy processing, or hanging prompt).
  3. Proactively ask the user if they want to **increase the timeout limit** (e.g., 2m, 5m), **terminate the task**, or **switch to an alternative approach**.

---

## Model Priority Matrix

For tasks that genuinely require language generation, conceptual reasoning, or code drafting:

1. **Tier 1: Free External Models (Groq / OpenRouter Free)**
   - Groq `openai/gpt-oss-120b`: Ultra high-speed reasoning and drafting (~300 T/s).
   - Cohere `cohere/north-mini-code:free`: Specialized code synthesis and bug fixing.
   - Nemotron Ultra `nvidia/nemotron-3-ultra-550b-a55b:free`: Massive 550B model for deep architectural reasoning.
   - Gemma 4 `google/gemma-4-31b-it:free`: Balanced general queries and documentation.
   - Nemotron Lightning `nvidia/nemotron-3.5-lightning:free`: Fast multi-turn logic.

2. **Tier 2: GPT & Claude Models (External Paid/Configured)**
   - Used when tasks specifically require OpenAI (`gpt-4o`, `o1`, `o3`) or Anthropic (`claude-3-5-sonnet`) models.

3. **Tier 3: Lightweight Gemini (`flash_lite` / `flash`)**
   - Subagents are always spawned with `Model: 'flash_lite'` or `'flash'`.
   - Never default to heavy `Model: 'pro'`.

---

## Execution Utility

Use `router.py` to dispatch generation and reasoning tasks:

```bash
~/.gemini/config/plugins/auto-orchestrator/skills/auto-orchestrator/scripts/router.py -t <code|reasoning|fast|general> "<prompt>"
```

### Options:
- `-t code`: Prefers Cohere Code -> Groq -> Nemotron Ultra
- `-t reasoning`: Prefers Nemotron Ultra 550B -> Groq -> Nemotron Lightning
- `-t fast`: Prefers Groq 120B -> Nemotron Lightning
- `-m <model_name>`: Explicitly force a specific model alias or OpenRouter/OpenAI/Anthropic ID
- `-f <file>`: Read prompt from file
