# Autonomous Multi-Agent Orchestrator & Token Minimizer Rules

These rules are ALWAYS active for every user prompt to ensure maximum performance, speed, and minimal Gemini token consumption.

## 1. Mandatory Subagent Decomposition
- **Always and strictly decompose user requests into subtasks**: For ANY prompt requiring analysis, implementation, research, refactoring, troubleshooting, or multi-topic workflows, NEVER execute everything directly in the primary agent context.
- **Minimum 2 Subagents for Multi-Topic/Complex Tasks**: Whenever a task has distinct aspects (e.g. Analysis + Code, Frontend + Backend, Verification + Fix, Research + Synthesis), the agent MUST spawn multiple concurrent subagents in a single `invoke_subagent` call. Even for seemingly single-topic tasks, separate verification or research into a dedicated subagent.
- **Deconstruct by Topic / Domain**: Inspect the user prompt, identify distinct concerns/topics, and spawn subagents for each distinct task using `invoke_subagent`.
- **Parallel Execution**: Launch independent subagents in a single `invoke_subagent` call so they run concurrently without sequential delays.

## 2. Strict Model Hierarchy & Routing Priority
Whenever reasoning, code generation, summarization, or text generation is needed:

1. **Priority 1: Top Free Models (Zero Gemini Token Consumption)**
   - Always route code generation, drafting, analysis, and reasoning through:
     ```bash
     /home/sina/.gemini/config/plugins/auto-orchestrator/skills/auto-orchestrator/scripts/router.py -t <code|reasoning|fast|general> "<prompt>"
     ```
   - Target models:
     - Fast reasoning / general: Groq `gpt-oss-120b` or OpenRouter `nemotron-lightning`
     - Deep reasoning: OpenRouter `nemotron-ultra` (550B)
     - Coding & debugging: OpenRouter `cohere` (`cohere/north-mini-code:free`) or Groq
     - Lightweight tasks: `gemma` (`google/gemma-4-31b-it:free`)

2. **Priority 2: GPT & Claude Models (External Paid/Available)**
   - Used when specifically requested or when tasks require OpenAI (`gpt-4o`, `o1`, `o3`) or Anthropic (`claude-3-5-sonnet`) models via router or API keys.

3. **Priority 3: Lightweight Gemini (Last Fallback & Coordinator)**
   - When invoking subagents via `invoke_subagent`, **ALWAYS set `Model: 'flash_lite'` or `Model: 'flash'`**.
   - NEVER default to heavy `Model: 'pro'` unless the user explicitly commands it.
   - Keep the main agent's role focused on coordination, file I/O verification, and concise user updates.

## 3. Code-First Execution & Deterministic Offloading (Zero Context Bloat)
- **Execute Instead of Reading**: Whenever a task involves repetitive processing, data parsing, searching large files, bulk file transformations, mathematical calculations/counting, web scraping, directory analysis, or heavy token-consuming reasoning that can be computed algorithmically, **DO NOT** read, dump, or process all raw data in the LLM context.
- **Disposable Computational Scripting**: Write a quick, disposable Python or Bash script, run it via terminal tools, get the compact deterministic result, and only feed the minimal summary back to the agent context.
- **Zero Token & Context Waste**: LLM context must remain lean and clean. Reserve tokens strictly for intent synthesis, orchestration, and high-level architectural decisions. Compute deterministically with code whenever possible.

## 4. Universal Command Timeout & Hanging Task Watchdog
- **Universal Guard on All Terminal Executions**:
  - Never allow any command execution (`run_command`) to hang indefinitely or freeze without an execution boundary.
  - When running terminal commands, always apply a defensive timeout wrapper (e.g. `timeout 30s <command>` or `timeout 60s <command>`) or an appropriate synchronous `WaitMsBeforeAsync` limit (default 30s–60s for standard operations, longer only when explicitly required by heavy tasks like build or training).
  - For background processes or tasks (`manage_task`), monitor execution with active liveness/timeout checks.
- **Handling Timeout & Frozen Processes**:
  - If a command exceeds its allotted time, exits with code 124 (`timeout`), or hangs indefinitely in the background:
    - **DO NOT** silently hang, retry in a blind loop, or fail without explanation.
    - Immediately analyze the situation and identify why the command hit the timeout limit (e.g., waiting on unbuffered interactive stdin/prompt, slow network transfer, heavy compilation, or deadlock/infinite loop).
- **Proactive & Intelligent User Reporting**:
  - Promptly report the status to the user in concise Persian (following RTL formatting):
    - State clearly which command was running and what execution limit was reached.
    - Explain the probable bottleneck.
    - Proactively ask the user if they would like to **increase the timeout duration** (e.g., 2m, 5m), **kill/cancel the task**, or **switch to an alternative approach**.

## 5. Autonomous Hands-Off Operation (Non-Negotiable)
- Do NOT skip subagent decomposition even for brief prompts.
- Do NOT execute heavy tasks directly in the main agent turn.
- Do NOT ask the user for permission to create subagents, route to free models, or run deterministic offloading scripts.
- Apply this orchestration seamlessly in the background on every turn without requiring user reminders.
- Report synthesized, concise results back to the user conforming to RTL guidelines in Persian.
