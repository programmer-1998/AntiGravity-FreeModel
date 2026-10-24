---
name: auto-orchestrator
description: >-
  Autonomous task decomposition and multi-agent orchestrator. Automatically splits user prompts into subagents,
  routes tasks through a hierarchical model selector (Priority 1: Free models like Groq, Nemotron, Cohere;
  Priority 2: GPT/Claude; Priority 3: Lightweight Gemini like flash_lite/flash), minimizing token consumption and accelerating responses.
---

# Auto-Orchestrator Skill

This skill governs the autonomous division of labor across subagents and external models to maximize speed and minimize Gemini token consumption.

## Architecture

```
User Prompt
    │
    ▼
[Decomposer & Task Classifier]
    │
    ├── Task 1 (e.g. Code Implementation) ──> Subagent (Model: flash_lite) ──> Router (Cohere Code / Groq)
    ├── Task 2 (e.g. Deep Architecture)    ──> Subagent (Model: flash_lite) ──> Router (Nemotron Ultra 550B)
    └── Task 3 (e.g. Quick Tests / Docs)   ──> Subagent (Model: flash_lite) ──> Router (Groq GPT-OSS-120B)
    │
    ▼
[Main Agent: Synthesizer & Coordinator]
    │
    ▼
Final Response to User (Persian RTL)
```

## Model Priority Matrix

1. **Tier 1: Free External Models (Groq / OpenRouter Free)**
   - Groq `openai/gpt-oss-120b`: Ultra high-speed reasoning and drafting.
   - Cohere `cohere/north-mini-code:free`: Specialized code synthesis and bug fixing.
   - Nemotron Ultra `nvidia/nemotron-3-ultra-550b-a55b:free`: Massive 550B model for deep architectural reasoning.
   - Gemma 4 `google/gemma-4-31b-it:free`: Balanced general queries.
   - Nemotron Lightning `nvidia/nemotron-3.5-lightning:free`: Fast multi-turn logic.

2. **Tier 2: GPT & Claude Models (External Paid/Configured)**
   - Used when tasks specifically require OpenAI (`gpt-4o`, `o1`, `o3`) or Anthropic (`claude-3-5-sonnet`) models.

3. **Tier 3: Lightweight Gemini (`flash_lite` / `flash`)**
   - Subagents are always spawned with `Model: 'flash_lite'` or `'flash'`.
   - Never default to heavy `Model: 'pro'`.

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
