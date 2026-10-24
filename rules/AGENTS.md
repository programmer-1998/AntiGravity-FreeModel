# Autonomous Multi-Agent Orchestrator & Token Minimizer Rules

These rules are ALWAYS active for every user prompt to ensure maximum performance, speed, and minimal Gemini token consumption.

## 1. Mandatory Subagent Decomposition
- **Always and strictly decompose user requests into subtasks**: For any prompt requiring analysis, implementation, research, refactoring, or multi-topic workflows, NEVER execute everything directly in the primary agent context.
- **Deconstruct by Topic / Domain**: Inspect the user prompt, identify distinct concerns/topics (e.g., frontend vs backend, research vs coding, testing vs architecture), and spawn subagents for each distinct task using `invoke_subagent`.
- **Parallel Execution**: Launch independent subagents in a single `invoke_subagent` call so they run concurrently.

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

## 3. Autonomous Hands-Off Operation
- Do NOT ask the user for permission to create subagents or to route to free models.
- Apply this orchestration seamlessly in the background on every turn without requiring user reminders.
- Report synthesized, concise results back to the user conforming to RTL guidelines in Persian.
