# Grok 4.1 Fast Reasoning — How to Use

This is a standalone Python script to chat with the **Grok 4.1 Fast Reasoning** model (or any OpenAI-compatible endpoint) directly from your terminal. No project setup, no config copying into repos.

---

## 1. Install the dependency

You only need the `openai` Python package. Run this once:

```powershell
pip install openai
```

Or if you use `uv`:

```powershell
uv pip install openai
```

---

## 2. Set up your credentials (pick one)

### Option A — Environment variables (recommended for daily use)

```powershell
# Set these in your PowerShell profile ($PROFILE) or run before each session
$env:AZURE_GROK_ENDPOINT = "https://your-endpoint.eastus.models.ai.azure.com"
$env:AZURE_GROK_KEY      = "your-api-key-here"
$env:AZURE_GROK_MODEL    = "grok-4-1-fast-reasoning"
```

### Option B — Config file

Create `%USERPROFILE%\.grokrc` with this content:

```json
{
  "endpoint": "https://your-endpoint.eastus.models.ai.azure.com",
  "api_key": "your-api-key-here",
  "model": "grok-4-1-fast-reasoning"
}
```

**Security:** This file is in your home folder, outside any git repo. The `.gitignore` in this folder also excludes it as a safety net.

---

## 3. Run it

Open a terminal in this folder:

```powershell
cd C:\Users\juliu\source\repos\Coding-AI-Scripts\Grok-4-1-fast-reasoning
```

### Basic question

```powershell
python grok-chat.py "Explain quantum computing in simple terms"
```

### With a system prompt (sets the AI's behavior)

```powershell
python grok-chat.py --system "You are a senior code reviewer" "Review this Python function: def add(a,b): return a+b"
```

### Pipe input from another command

```powershell
type myfile.txt | python grok-chat.py
```

### Or from anywhere (if the folder is in your PATH)

```powershell
grok-chat.py "What is the capital of France?"
```

---

## 4. Example outputs

```powershell
> python grok-chat.py "Write a one-line joke about programming"
Why do programmers prefer dark mode? Because light attracts bugs.
```

```powershell
> python grok-chat.py --system "Answer in exactly 5 words" "What is Rust?"
A safe systems programming language.
```

---

## What NOT to do

| ❌ Don't | ✅ Do |
|---|---|
| Commit API keys to git | Use env vars or `~/.grokrc` |
| Copy the script into every repo | Keep it here, call it by path |
| Share `~/.grokrc` with anyone | Keep it secret, keep it safe |
| Run without `pip install openai` first | Install the dependency once |

---

## Troubleshooting

| Error | Fix |
|---|---|
| `openai package not installed` | Run `pip install openai` |
| `No endpoint configured` | Set `AZURE_GROK_ENDPOINT` or create `~/.grokrc` |
| `401` or auth errors | Check `AZURE_GROK_KEY` is correct |
| `404` or model not found | Check model name and endpoint URL |

---

## File structure

```
Coding-AI-Scripts\
├── Grok-4-1-fast-reasoning\
│   ├── grok-chat.py       ← The script
│   ├── how-to-use.md      ← This file
│   └── .gitignore          ← Protects credentials
└── ... (future scripts go here)
```