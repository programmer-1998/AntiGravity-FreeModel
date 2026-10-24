# 🚀 AntiGravity-FreeModel

<p align="center">
  <b>Autonomous Multi-Agent Orchestrator & Free Model Router for Google Antigravity</b><br>
  <i>Slash your Gemini token consumption to zero while boosting coding speed by 10x with Groq LPUs and 550B Free Models.</i>
</p>

<p align="center">
  <a href="https://github.com/programmer-1998/AntiGravity-FreeModel/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License: MIT"></a>
  <a href="https://github.com/programmer-1998/AntiGravity-FreeModel"><img src="https://img.shields.io/badge/Antigravity-2.0%2B-purple.svg?style=for-the-badge" alt="Antigravity"></a>
  <a href="https://groq.com"><img src="https://img.shields.io/badge/Groq-LPU%20UltraFast-orange.svg?style=for-the-badge" alt="Groq"></a>
  <a href="https://openrouter.ai"><img src="https://img.shields.io/badge/OpenRouter-100%25%20Free%20Tier-green.svg?style=for-the-badge" alt="OpenRouter"></a>
  <img src="https://img.shields.io/badge/Gemini%20Tokens-Preserved-brightgreen.svg?style=for-the-badge" alt="Token Preserved">
</p>

---

## 🌟 Overview

**AntiGravity-FreeModel** is a native plugin and autonomous orchestrator designed specifically for **Google Antigravity**. 

Instead of burning your valuable Gemini quotas on heavy code synthesis, debugging, and repetitive drafting, this plugin enforces **automatic subagent decomposition** at the IDE rule level and offloads heavy tasks to **100% free, ultra-fast external models** (Groq LPUs, NVIDIA Nemotron 550B, Cohere Code, and Gemma).

> 💡 **You never have to remind Antigravity in chat!**  
> Simply type your prompt normally. The system automatically inspects your task, breaks it down into topic-specific subagents, routes code/reasoning to free models, and uses lightweight Gemini (`flash_lite`) strictly as the orchestrator.

---

## 🏗️ Architecture & Workflow

```
                        ┌─────────────────────────────────┐
                        │      Your Prompt in Chat        │
                        └────────────────┬────────────────┘
                                         │
                                         ▼
                        ┌─────────────────────────────────┐
                        │    Antigravity Orchestrator     │
                        │    (Gemini 3.8 Flash-Lite)      │
                        │   Rules enforce auto-splitting   │
                        └───────┬───────────────┬─────────┘
                                │               │
              ┌─────────────────┘               └─────────────────┐
              ▼                                                   ▼
 ┌─────────────────────────┐                         ┌─────────────────────────┐
 │ Subagent 1: Coder       │                         │ Subagent 2: Architect   │
 │ Task: Implement & Debug │                         │ Task: Deep Logic & Spec │
 └────────────┬────────────┘                         └────────────┬────────────┘
              │                                                   │
              ▼                                                   ▼
 ┌─────────────────────────┐                         ┌─────────────────────────┐
 │ Cohere Code / Groq LPU  │                         │ Nemotron Ultra 550B     │
 │ (100% Free / Zero Token)│                         │ (100% Free / Zero Token)│
 └────────────┬────────────┘                         └────────────┬────────────┘
              │                                                   │
              └─────────────────┬───────────────┬─────────────────┘
                                │               │
                                ▼               ▼
                        ┌─────────────────────────────────┐
                        │  Workspace Diffs & Verification │
                        │      Synthesized Response       │
                        └─────────────────────────────────┘
```

---

## ⚡ Key Highlights

- **💸 Zero Gemini Token Burn for Heavy Lifting**: Heavy generation, boilerplate creation, unit testing, and reasoning are routed to free external engines.
- **⚡ 10x Inference Speed via Groq LPUs**: Groq’s custom Language Processing Units stream hundreds of tokens per second.
- **🧠 550B Parameter Reasoning**: Tap into `nvidia/nemotron-3-ultra-550b-a55b:free` without paying a single cent.
- **🤖 Autonomous Subagent Decomposition**: Prompts are dynamically split into parallel subagents according to topic domain.
- **🔄 Resilient Auto-Cascade**: If a provider hits temporary rate-limits or network blips, the built-in router automatically cascades to the next best free model in real-time.
- **🔒 Privacy & Local Configuration**: Your personal API keys stay on your machine in `config.env`.

---

## 📊 Model Hierarchy & Capabilities

| Priority | Model | Provider | Strengths & Best Use | Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | **`cohere/north-mini-code`** | OpenRouter | Code writing, refactoring, bug fixes, regex | **Free** |
| **Tier 1** | **`openai/gpt-oss-120b`** | Groq LPU | Ultra-fast drafting, general reasoning, scripts | **Free** |
| **Tier 1** | **`nvidia/nemotron-3-ultra`** (550B) | OpenRouter | Deep system design, complex math, architecture | **Free** |
| **Tier 1** | **`google/gemma-4-31b-it`** | OpenRouter | Explanations, lightweight tasks, translations | **Free** |
| **Tier 2** | **GPT-4o / Claude 3.5 Sonnet** | OpenAI / Anthropic | Optional fallback when specific paid models requested | Paid |
| **Tier 3** | **Gemini 3.8 Flash-Lite** | Antigravity Native | Workspace file IO, git diffs, coordinator only | Native |

---

## 📥 Quick Installation (1-Minute Setup)

### Method 1: Automatic Installer (Recommended)

Run this one-line command in your terminal:

```bash
git clone https://github.com/programmer-1998/AntiGravity-FreeModel.git ~/.gemini/config/plugins/auto-orchestrator && cd ~/.gemini/config/plugins/auto-orchestrator && ./install.sh
```

### Method 2: Manual Setup

1. **Clone into Antigravity Plugins directory**:
   ```bash
   git clone https://github.com/programmer-1998/AntiGravity-FreeModel.git ~/.gemini/config/plugins/auto-orchestrator
   ```

2. **Set up your configuration**:
   ```bash
   cd ~/.gemini/config/plugins/auto-orchestrator
   cp config.env.example config.env
   ```

3. **Add your free API keys in `config.env`** (see below).

4. **Restart Antigravity or open a new chat** — the plugin is immediately live!

---

## 🔑 Obtaining Free API Keys (Zero Credit Card Required)

### 1. Groq Cloud (Ultra-Fast Inference)
1. Go to [console.groq.com/keys](https://console.groq.com/keys).
2. Sign in with GitHub or Google.
3. Click **Create API Key**, copy it, and paste it into `config.env`:
   ```env
   GROQ_API_KEY="gsk_..."
   ```

### 2. OpenRouter (Access to 550B Nemotron & Cohere Code)
1. Go to [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys).
2. Sign in and click **Create Key**.
3. Copy the key and paste it into `config.env`:
   ```env
   OPENROUTER_API_KEY="sk-or-v1-..."
   ```
*(Note: OpenRouter does not require adding credits to use any model with the `:free` suffix).*

---

## 🛠️ CLI Direct Usage

You or your subagents can also query the multi-model cascade directly from the terminal:

```bash
# Code generation task (routes to Cohere Code -> Groq -> Nemotron)
~/.gemini/config/plugins/auto-orchestrator/skills/auto-orchestrator/scripts/router.py -t code "Write a JWT authentication middleware in FastAPI"

# Fast reasoning task (routes to Groq 120B)
~/.gemini/config/plugins/auto-orchestrator/skills/auto-orchestrator/scripts/router.py -t fast "Explain the difference between TCP and UDP"

# Explicitly select a model
~/.gemini/config/plugins/auto-orchestrator/skills/auto-orchestrator/scripts/router.py -m nemotron-ultra "Analyze this microservices architectural trade-off"
```

---

<div dir="rtl">

## 🇮🇷 راهنمای فارسی (AntiGravity-FreeModel)

این پلاگین با هدف **به حداقل رساندن مصرف توکن‌های جمنای** و **افزایش ۱۰ برابری سرعت کدنویسی** در گوگل آنتی‌گرویتی (Antigravity) طراحی شده است.

### ویژگی‌های کلیدی:
1. **شکستن خودکار تسک‌ها به ساب‌ایجنت‌ها**: هر پرامپتی که ارسال کنید، سیستم به صورت خودکار موضوعات را تفکیک کرده و ساب‌ایجنت‌های مجزا برای آن ایجاد می‌کند.
2. **استفاده از مدل‌های کاملاً رایگان**:
   - برای کدنویسی و دیباگ: مدل‌های قدرتمند `cohere/north-mini-code:free` یا `groq`
   - برای استدلال عمیق و معماری: مدل غول‌پیکر ۵۵۰ میلیاردی `nvidia/nemotron-3-ultra-550b-a55b:free`
   - برای پاسخ‌های آنی: مدل فوق‌سریع ۱۲۰ میلیاردی `Groq LPU`
3. **حفظ توکن‌های اصلی جمنای**: جمنای صرفاً در نقش سبک (`flash_lite`) به عنوان مدیر ساب‌ایجنت‌ها و مدیریت فایل‌ها عمل می‌کند و توکن‌های سنگین مصرف نمی‌شود.
4. **سوئیچینگ خودکار (Fallback)**: در صورت بروز هرگونه اختلال یا محدودیت در یک مدل، روتر به صورت خودکار به مدل رایگان بعدی سوئیچ می‌کند.

### مراحل نصب:
```bash
git clone https://github.com/programmer-1998/AntiGravity-FreeModel.git ~/.gemini/config/plugins/auto-orchestrator
cd ~/.gemini/config/plugins/auto-orchestrator
cp config.env.example config.env
```
سپس کلیدهای رایگان خود را در فایل `config.env` وارد کنید.

</div>

---

## 🤝 Contributing

Contributions, feature requests, and PRs are warmly welcome! Feel free to open an issue or submit a pull request.

## 📄 License

This project is licensed under the [MIT License](LICENSE).
