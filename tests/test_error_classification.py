"""Tests for core/error_classification.py — error taxonomy and classification."""

from __future__ import annotations

import socket
import ssl

import pytest

from core.error_classification import (
    ErrorCategory,
    backoff_for,
    classify_error,
    error_summary,
    max_retries_for,
    should_halt,
    should_retry,
)


class TestClassifyError:
    def test_connection_error_is_transient(self) -> None:
        assert classify_error(ConnectionError("boom")) == ErrorCategory.TRANSIENT

    def test_timeout_error_is_transient(self) -> None:
        assert classify_error(TimeoutError("slow")) == ErrorCategory.TRANSIENT

    def test_socket_timeout_is_transient(self) -> None:
        assert classify_error(socket.timeout("slow")) == ErrorCategory.TRANSIENT

    def test_ssl_error_is_transient(self) -> None:
        assert classify_error(ssl.SSLError("cert")) == ErrorCategory.TRANSIENT

    def test_os_error_is_transient(self) -> None:
        assert classify_error(OSError("io")) == ErrorCategory.TRANSIENT

    def test_permission_error_is_permission(self) -> None:
        assert classify_error(PermissionError("no")) == ErrorCategory.PERMISSION

    def test_file_not_found_is_configuration(self) -> None:
        assert classify_error(FileNotFoundError("missing")) == ErrorCategory.CONFIGURATION

    def test_import_error_is_configuration(self) -> None:
        assert classify_error(ImportError("bad")) == ErrorCategory.CONFIGURATION

    def test_key_error_is_configuration(self) -> None:
        assert classify_error(KeyError("key")) == ErrorCategory.CONFIGURATION

    def test_value_error_is_configuration(self) -> None:
        assert classify_error(ValueError("bad")) == ErrorCategory.CONFIGURATION

    def test_assertion_error_is_verification(self) -> None:
        assert classify_error(AssertionError("fail")) == ErrorCategory.VERIFICATION

    def test_memory_error_is_fatal(self) -> None:
        assert classify_error(MemoryError("oom")) == ErrorCategory.FATAL

    def test_recursion_error_is_fatal(self) -> None:
        assert classify_error(RecursionError("deep")) == ErrorCategory.FATAL

    def test_not_implemented_is_fatal(self) -> None:
        assert classify_error(NotImplementedError("todo")) == ErrorCategory.FATAL

    def test_runtime_error_is_fatal(self) -> None:
        assert classify_error(RuntimeError("panic")) == ErrorCategory.FATAL

    def test_unmapped_exception_is_fatal(self) -> None:
        class CustomError(Exception):
            pass

        assert classify_error(CustomError("?")) == ErrorCategory.FATAL

    def test_subclass_inherits_parent(self) -> None:
        class MyConnectionError(ConnectionError):
            pass

        assert classify_error(MyConnectionError("boom")) == ErrorCategory.TRANSIENT


class TestRetryStrategy:
    def test_should_retry_transient(self) -> None:
        assert should_retry(ErrorCategory.TRANSIENT) is True

    def test_should_retry_recoverable(self) -> None:
        assert should_retry(ErrorCategory.RECOVERABLE) is True

    def test_should_retry_verification(self) -> None:
        assert should_retry(ErrorCategory.VERIFICATION) is True

    def test_should_not_retry_configuration(self) -> None:
        assert should_retry(ErrorCategory.CONFIGURATION) is False

    def test_should_not_retry_permission(self) -> None:
        assert should_retry(ErrorCategory.PERMISSION) is False

    def test_should_not_retry_fatal(self) -> None:
        assert should_retry(ErrorCategory.FATAL) is False


class TestHaltStrategy:
    def test_should_halt_configuration(self) -> None:
        assert should_halt(ErrorCategory.CONFIGURATION) is True

    def test_should_halt_permission(self) -> None:
        assert should_halt(ErrorCategory.PERMISSION) is True

    def test_should_halt_fatal(self) -> None:
        assert should_halt(ErrorCategory.FATAL) is True

    def test_should_not_halt_transient(self) -> None:
        assert should_halt(ErrorCategory.TRANSIENT) is False

    def test_should_not_halt_recoverable(self) -> None:
        assert should_halt(ErrorCategory.RECOVERABLE) is False

    def test_should_not_halt_verification(self) -> None:
        assert should_halt(ErrorCategory.VERIFICATION) is False


class TestRetryConfig:
    def test_max_retries_transient(self) -> None:
        assert max_retries_for(ErrorCategory.TRANSIENT) == 5

    def test_max_retries_recoverable(self) -> None:
        assert max_retries_for(ErrorCategory.RECOVERABLE) == 3

    def test_max_retries_verification(self) -> None:
        assert max_retries_for(ErrorCategory.VERIFICATION) == 3

    def test_max_retries_default(self) -> None:
        assert max_retries_for(ErrorCategory.FATAL, default=1) == 1

    def test_backoff_transient(self) -> None:
        assert backoff_for(ErrorCategory.TRANSIENT) == 1.0

    def test_backoff_recoverable(self) -> None:
        assert backoff_for(ErrorCategory.RECOVERABLE) == 2.0

    def test_backoff_verification(self) -> None:
        assert backoff_for(ErrorCategory.VERIFICATION) == 1.5

    def test_backoff_default(self) -> None:
        assert backoff_for(ErrorCategory.FATAL, default=0.5) == 0.5


class TestErrorSummary:
    def test_summary_structure(self) -> None:
        summary = error_summary(ValueError("bad input"))
        assert summary["type"] == "ValueError"
        assert summary["message"] == "bad input"
        assert summary["category"] == "configuration"

    def test_summary_for_transient(self) -> None:
        summary = error_summary(TimeoutError("slow"))
        assert summary["category"] == "transient"
