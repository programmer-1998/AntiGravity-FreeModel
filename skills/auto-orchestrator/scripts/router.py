#!/usr/bin/env python3
"""
Multi-Model Router & Cascade Runner for AntiGravity
Priority 1: Top Free Models (Groq GPT-OSS-120B, Nemotron Ultra 550B, Cohere Code, Gemma 4, Nemotron Lightning)
Priority 2: GPT & Claude (OpenAI / Anthropic APIs or OpenRouter)
Priority 3: Fallback / Lightweight Gemini

Loads API keys securely from environment variables or a local config.env file.
NO personal API keys are hardcoded.
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.error

def load_env_file(filepath):
    """Parse a simple .env / config.env file and load into os.environ if not already set."""
    if not os.path.isfile(filepath):
        return False
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key and key not in os.environ:
                        os.environ[key] = val
        return True
    except Exception as e:
        sys.stderr.write(f"Warning: Failed to parse config file '{filepath}': {e}\n")
        return False

def discover_and_load_config():
    """Look for config.env in multiple standard locations."""
    candidates = []
    
    # 1. Custom path from env
    if "CONFIG_ENV_PATH" in os.environ:
        candidates.append(os.environ["CONFIG_ENV_PATH"])
    
    # 2. Current working directory
    candidates.append(os.path.join(os.getcwd(), "config.env"))
    
    # 3. Repository / Plugin root directory relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    candidates.append(os.path.join(plugin_root, "config.env"))
    candidates.append(os.path.join(script_dir, "config.env"))

    # 4. Standard ~/.gemini/config/plugins/auto-orchestrator/config.env location
    candidates.append(os.path.expanduser("~/.gemini/config/plugins/auto-orchestrator/config.env"))
    candidates.append(os.path.expanduser("~/.gemini/config/config.env"))

    for c in candidates:
        if os.path.isfile(c):
            load_env_file(c)
            break

# Load configuration if available
discover_and_load_config()

GROQ_KEY = os.environ.get("GROQ_API_KEY", "").strip()
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()

# Model Aliases & Configurations
FREE_MODELS = {
    "groq": {"provider": "groq", "model": "openai/gpt-oss-120b", "name": "Groq GPT-OSS-120B"},
    "gpt-oss-120b": {"provider": "groq", "model": "openai/gpt-oss-120b", "name": "Groq GPT-OSS-120B"},
    "groq-qwen": {"provider": "groq", "model": "qwen/qwen3.8-27b", "name": "Groq Qwen 3.8 27B"},
    "nemotron-ultra": {"provider": "openrouter", "model": "nvidia/nemotron-3-ultra-550b-a55b:free", "name": "Nemotron Ultra 550B Free"},
    "nemotron": {"provider": "openrouter", "model": "nvidia/nemotron-3.5-lightning:free", "name": "Nemotron 3.5 Lightning Free"},
    "nemotron-lightning": {"provider": "openrouter", "model": "nvidia/nemotron-3.5-lightning:free", "name": "Nemotron 3.5 Lightning Free"},
    "cohere": {"provider": "openrouter", "model": "cohere/north-mini-code:free", "name": "Cohere North Mini Code Free"},
    "cohere-code": {"provider": "openrouter", "model": "cohere/north-mini-code:free", "name": "Cohere North Mini Code Free"},
    "gemma": {"provider": "openrouter", "model": "google/gemma-4-31b-it:free", "name": "Gemma 4 31B Free"},
    "laguna": {"provider": "openrouter", "model": "poolside/laguna-s-2.1:free", "name": "Poolside Laguna S 2.1 Free"},
}

TASK_DEFAULTS = {
    "code": ["cohere", "groq", "nemotron-ultra", "gemma"],
    "reasoning": ["nemotron-ultra", "groq", "nemotron", "gemma"],
    "fast": ["groq", "nemotron", "cohere"],
    "general": ["groq", "nemotron-ultra", "nemotron", "gemma"],
}

def query_groq(model_id, prompt, system_prompt=None):
    if not GROQ_KEY:
        raise ValueError("GROQ_API_KEY is not set. Set it in your environment or in config.env.")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    }
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    data = {"model": model_id, "messages": messages}
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        msg = res.get("choices", [{}])[0].get("message", {})
        return msg.get("content") or msg.get("reasoning", "")

def query_openrouter(model_id, prompt, system_prompt=None):
    if not OPENROUTER_KEY:
        raise ValueError("OPENROUTER_API_KEY is not set. Set it in your environment or in config.env.")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    data = {"model": model_id, "messages": messages}
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=90) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        msg = res.get("choices", [{}])[0].get("message", {})
        return msg.get("content") or msg.get("reasoning", "")

def query_openai(model_id, prompt, system_prompt=None):
    if not OPENAI_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is not configured.")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    data = {"model": model_id, "messages": messages}
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["choices"][0]["message"]["content"]

def query_anthropic(model_id, prompt, system_prompt=None):
    if not ANTHROPIC_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not configured.")
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_id,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}]
    }
    if system_prompt:
        data["system"] = system_prompt

    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=90) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["content"][0]["text"]

def execute_single_target(target, prompt, system_prompt=None):
    target_clean = target.lower()
    if target_clean in FREE_MODELS:
        cfg = FREE_MODELS[target_clean]
        if cfg["provider"] == "groq":
            return query_groq(cfg["model"], prompt, system_prompt)
        elif cfg["provider"] == "openrouter":
            return query_openrouter(cfg["model"], prompt, system_prompt)
    elif target_clean.startswith("gpt-") or target_clean.startswith("o1") or target_clean.startswith("o3"):
        if OPENAI_KEY:
            return query_openai(target, prompt, system_prompt)
        elif OPENROUTER_KEY:
            return query_openrouter(f"openai/{target}", prompt, system_prompt)
        else:
            raise ValueError("Neither OPENAI_API_KEY nor OPENROUTER_API_KEY is configured for OpenAI model query.")
    elif "claude" in target_clean:
        if ANTHROPIC_KEY:
            return query_anthropic(target, prompt, system_prompt)
        elif OPENROUTER_KEY:
            return query_openrouter(f"anthropic/{target}", prompt, system_prompt)
        else:
            raise ValueError("Neither ANTHROPIC_API_KEY nor OPENROUTER_API_KEY is configured for Anthropic model query.")
    elif ":" in target or "/" in target:
        return query_openrouter(target, prompt, system_prompt)
    else:
        # Default fallback to groq
        return query_groq("openai/gpt-oss-120b", prompt, system_prompt)

def run_cascade(targets, prompt, system_prompt=None):
    failures = []
    for t in targets:
        try:
            output = execute_single_target(t, prompt, system_prompt)
            if output and output.strip():
                return output, t
        except Exception as e:
            failures.append(f"{t}: {str(e)}")
            continue
    summary_errors = "\n  - ".join(failures)
    raise RuntimeError(
        f"All cascaded models failed.\nAttempted models:\n  - {summary_errors}\n\n"
        "Please ensure GROQ_API_KEY and/or OPENROUTER_API_KEY are properly configured in environment variables or in config.env."
    )

def main():
    parser = argparse.ArgumentParser(description="Multi-Model Subagent & Task Router")
    parser.add_argument("--model", "-m", help="Target model alias (groq, nemotron-ultra, cohere, gemma, gpt-4o, etc.)")
    parser.add_argument("--type", "-t", choices=["code", "reasoning", "fast", "general"], default="general", help="Task type")
    parser.add_argument("--system", "-s", help="Optional system prompt")
    parser.add_argument("--file", "-f", help="Read prompt from file")
    parser.add_argument("prompt_parts", nargs="*", help="Prompt text")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            prompt = f.read()
    elif args.prompt_parts:
        prompt = " ".join(args.prompt_parts)
    elif not sys.stdin.isatty():
        prompt = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(1)

    if not prompt.strip():
        print("Error: Empty prompt received.", file=sys.stderr)
        sys.exit(1)

    # Determine cascade order
    if args.model:
        targets = [args.model]
        # Append backups
        for bk in TASK_DEFAULTS.get(args.type, ["groq", "nemotron-ultra"]):
            if bk != args.model:
                targets.append(bk)
    else:
        targets = TASK_DEFAULTS.get(args.type, TASK_DEFAULTS["general"])

    try:
        response, used_model = run_cascade(targets, prompt, args.system)
        print(response)
    except Exception as e:
        print(f"Router Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
