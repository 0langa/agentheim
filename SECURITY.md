# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| < main  | :x:                |

Agentheim is currently in active development. Only the latest commit on `main` receives security updates.

## Reporting a Vulnerability

If you discover a security vulnerability in Agentheim, please report it responsibly.

**Do NOT open a public issue.**

Instead, please send an email to the maintainer with:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge receipt within 48 hours and provide a timeline for a fix.

## Security Features

Agentheim is designed with security as a core principle:

- **Path confinement** — All filesystem operations are scoped to the workspace
- **Policy engine** — All tool invocations are gated by configurable risk policies
- **Secret redaction** — API keys and tokens are stripped from all logs and artifacts
- **Local-first** — By default, no data leaves your machine
- **Approval gates** — Destructive operations require explicit confirmation
- **Audit trail** — Every action is recorded in an append-only event ledger
