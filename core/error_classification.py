"""Error taxonomy and classification for the agentheim runtime.

Maps exceptions to canonical categories that drive retry strategy, alerting,
and graceful degradation.
"""

from __future__ import annotations

from enum import Enum
import socket
import ssl
from typing import Any


class ErrorCategory(Enum):
    """Canonical error categories.

    Each category maps to a runtime strategy:

    - TRANSIENT:    Exponential backoff + provider switch
    - RECOVERABLE:  Retry with same/mildly modified prompt
    - VERIFICATION: Enter FIX_LOOP (bounded retries)
    - CONFIGURATION: Halt + report
    - PERMISSION:   Log + request approval
    - FATAL:        Halt + preserve state
    """

    TRANSIENT = "transient"
    RECOVERABLE = "recoverable"
    VERIFICATION = "verification"
    CONFIGURATION = "configuration"
    PERMISSION = "permission"
    FATAL = "fatal"


# Exception-type → category mapping (most specific first)
_CATEGORY_MAP: dict[type[BaseException], ErrorCategory] = {
    # Transient (network / service flakes)
    ConnectionError: ErrorCategory.TRANSIENT,
    TimeoutError: ErrorCategory.TRANSIENT,
    socket.timeout: ErrorCategory.TRANSIENT,
    ssl.SSLError: ErrorCategory.TRANSIENT,
    OSError: ErrorCategory.TRANSIENT,

    # Permission
    PermissionError: ErrorCategory.PERMISSION,

    # Configuration
    FileNotFoundError: ErrorCategory.CONFIGURATION,
    ImportError: ErrorCategory.CONFIGURATION,
    ModuleNotFoundError: ErrorCategory.CONFIGURATION,
    KeyError: ErrorCategory.CONFIGURATION,
    ValueError: ErrorCategory.CONFIGURATION,

    # Verification
    AssertionError: ErrorCategory.VERIFICATION,

    # Fatal
    MemoryError: ErrorCategory.FATAL,
    RecursionError: ErrorCategory.FATAL,
    NotImplementedError: ErrorCategory.FATAL,
    RuntimeError: ErrorCategory.FATAL,
}


def classify_error(exc: BaseException) -> ErrorCategory:
    """Classify an exception into a canonical error category.

    Walks the exception's MRO and returns the first matching category.
    Falls back to FATAL for unmapped exceptions.
    """
    for cls in type(exc).__mro__:
        if cls in _CATEGORY_MAP:
            return _CATEGORY_MAP[cls]
    return ErrorCategory.FATAL


# ------------------------------------------------------------------
# Strategy helpers
# ------------------------------------------------------------------

def should_retry(category: ErrorCategory) -> bool:
    """Whether this category warrants automatic retry."""
    return category in {
        ErrorCategory.TRANSIENT,
        ErrorCategory.RECOVERABLE,
        ErrorCategory.VERIFICATION,
    }


def max_retries_for(category: ErrorCategory, default: int = 3) -> int:
    """Suggested max retry count per category."""
    return {
        ErrorCategory.TRANSIENT: 5,
        ErrorCategory.RECOVERABLE: 3,
        ErrorCategory.VERIFICATION: 3,
    }.get(category, default)


def backoff_for(category: ErrorCategory, default: float = 2.0) -> float:
    """Suggested initial backoff (seconds) per category."""
    return {
        ErrorCategory.TRANSIENT: 1.0,
        ErrorCategory.RECOVERABLE: 2.0,
        ErrorCategory.VERIFICATION: 1.5,
    }.get(category, default)


def should_halt(category: ErrorCategory) -> bool:
    """Whether this category should stop the run."""
    return category in {
        ErrorCategory.CONFIGURATION,
        ErrorCategory.PERMISSION,
        ErrorCategory.FATAL,
    }


def error_summary(exc: BaseException) -> dict[str, Any]:
    """Produce a JSON-safe summary of an exception for ledger payloads."""
    return {
        "type": type(exc).__name__,
        "message": str(exc),
        "category": classify_error(exc).value,
    }
