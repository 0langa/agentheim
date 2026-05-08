#!/usr/bin/env python3
"""grok-chat — CLI client for the Grok 4.1 Fast Reasoning model.

A standalone, self-contained Python script to call Grok (or any OpenAI-compatible
model endpoint) directly from any terminal. No project coupling, no config files
in your repos — credentials live in env vars or ~/.grokrc.

Usage:
    grok-chat "Your question here"
    grok-chat --system "You are an expert Python developer" "Review this code: ..."
    echo "Summarize this text" | grok-chat

Requires:
    pip install openai

Credentials (pick one):
    1. Environment variables:
       set AZURE_GROK_ENDPOINT=https://your-endpoint.eastus.models.ai.azure.com
       set AZURE_GROK_KEY=your-api-key
       set AZURE_GROK_MODEL=grok-4-1-fast-reasoning
    2. Config file at %USERPROFILE%\.grokrc:
       {"endpoint": "...", "api_key": "...", "model": "grok-4-1-fast-reasoning"}

Security notes:
    - API keys are NEVER stored in this script — read from env or ~/.grokrc
    - ~/.grokrc is excluded from git by .gitignore
    - Never commit credentials to version control
"""

import json
import os
import sys
from pathlib import Path

try:
    from openai import AzureOpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai", file=sys.stderr)
    sys.exit(1)


def _load_config() -> tuple[str, str, str]:
    """Load endpoint, key, model from env vars or ~/.grokrc."""
    endpoint = os.environ.get("AZURE_GROK_ENDPOINT")
    api_key = os.environ.get("AZURE_GROK_KEY")
    model = os.environ.get("AZURE_GROK_MODEL", "grok-4-1-fast-reasoning")

    if endpoint and api_key:
        return endpoint, api_key, model

    config_path = Path.home() / ".grokrc"
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text())
            endpoint = endpoint or data.get("endpoint")
            api_key = api_key or data.get("api_key")
            model = model or data.get("model", model)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Could not read ~/.grokrc: {e}", file=sys.stderr)

    if not endpoint:
        print(
            "Error: No endpoint configured. Set AZURE_GROK_ENDPOINT or create ~/.grokrc",
            file=sys.stderr,
        )
        sys.exit(1)
    if not api_key:
        print(
            "Error: No API key configured. Set AZURE_GROK_KEY or create ~/.grokrc",
            file=sys.stderr,
        )
        sys.exit(1)

    return endpoint, api_key, model


def main() -> None:
    endpoint, api_key, model = _load_config()

    # Parse args
    system_prompt = None
    args = sys.argv[1:]
    if args and args[0] == "--system" and len(args) >= 2:
        system_prompt = args[1]
        args = args[2:]

    # Get user message: args > stdin
    if args:
        user_message = " ".join(args)
    elif not sys.stdin.isatty():
        user_message = sys.stdin.read().strip()
    else:
        print("Usage: grok-chat [--system <prompt>] <message>", file=sys.stderr)
        sys.exit(1)

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2024-12-01-preview",
    )

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.0,
        )
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()