"""Secret redaction for logs, artifacts, and model context.

Replaces sensitive patterns with [REDACTED-<hash>] to preserve uniqueness
without leaking secrets.
"""

from __future__ import annotations

import hashlib
import re


SECRET_PATTERNS = [
    # API keys, tokens, passwords, secrets
    re.compile(r"(?i)(api[_-]?key|token|password|secret|auth)\s*[:=]\s*['\"]?([A-Za-z0-9_\-+/=]{8,}|[^\s'\"]{8,})"),
    # Connection strings
    re.compile(r"(?i)(connection\s*string)\s*[:=]\s*([^\n]+)"),
    # Private keys
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----.*?-----END [A-Z ]+PRIVATE KEY-----", re.DOTALL),
    # Certificates
    re.compile(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", re.DOTALL),
    # AWS access key ID
    re.compile(r"(?i)(AKIA[0-9A-Z]{16})"),
    # Generic hex tokens (64+ chars)
    re.compile(r"\b([a-f0-9]{64,})\b"),
    # Bearer tokens
    re.compile(r"(?i)(bearer\s+)([a-zA-Z0-9_\-./=]+)"),
]


def _hash_secret(secret: str) -> str:
    """Create a short deterministic hash for a secret."""
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()[:8]


def redact_text(text: str) -> str:
    """Redact secrets from text, replacing with [REDACTED-<hash>]."""
    redacted = text
    for pattern in SECRET_PATTERNS:

        def replacer(match: re.Match) -> str:
            # Find the secret portion of the match
            groups = match.groups()
            if len(groups) >= 2:
                # First group is label, second is secret
                secret = groups[-1]
                return f"{groups[0]}[REDACTED-{_hash_secret(secret)}]"
            # Single group or full match
            secret = match.group(0)
            return f"[REDACTED-{_hash_secret(secret)}]"

        redacted = pattern.sub(replacer, redacted)
    return redacted


def redact_dict(data: dict | list) -> dict | list:
    """Recursively redact secrets from a JSON-serializable structure."""
    if isinstance(data, str):
        return redact_text(data)
    if isinstance(data, dict):
        return {k: redact_dict(v) for k, v in data.items()}
    if isinstance(data, list):
        return [redact_dict(item) for item in data]
    return data
