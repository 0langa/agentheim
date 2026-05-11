# Project Overview

## Python Modules

### `fix_imports.py`
- Classes: none
- Functions: fix_imports_in_file, main
- Imports: pathlib, re

### `config\config.py`
- Classes: ModelRole, ProviderConfig, ModelConfig, AgentModelConfig, TeamConfig
- Functions: redact_secret, _provider_env_prefix, _load_provider, _load_registry_config, _load_legacy_grok_config, load_team_config, redacted_dict, redacted_dict, redacted_dict, resolve_role, by_role, dump
- Imports: __future__, core.errors, enum, json, os, pydantic, re, typing

### `core\agent_protocol.py`
- Classes: AgentMessage, AgentRequest, AgentResponse, AgentContext
- Functions: to_dict, from_step_context
- Imports: __future__, core.events, core.ledger, core.policy_engine, core.tool_protocol, dataclasses, pathlib, typing

### `core\approval_workflow.py`
- Classes: ApprovalRequest, ApprovalWorkflow
- Functions: from_decision, to_dict, request, grant, deny, get_pending, list_pending
- Imports: __future__, core.events, core.ledger, core.policy_engine, core.redaction, core.tool_protocol, dataclasses, datetime, typing, uuid

### `core\artifact_store.py`
- Classes: ArtifactSpec, ArtifactStore
- Functions: _is_valid_json, _is_valid_jsonl, __init__, create_run, validate_completeness, is_complete, list_artifacts, _produce_run_json, _produce_config_redacted, produce_context_artifacts, produce_plan, produce_final_report, produce_verification, produce_patch
- Imports: __future__, core.redaction, dataclasses, datetime, json, pathlib, typing

### `core\capability_registry.py`
- Classes: RegistryEntry, CapabilityRegistry
- Functions: get_registry, register_workflow, register_preset, register_memory_backend, get_workflow, list_workflows, get_preset, list_presets, get_memory_backend, list_memory_backends, __init__, register, get, list_by_kind, ids_by_kind, has, build
- Imports: __future__, dataclasses, typing

### `core\cascading_router.py`
- Classes: ModelBinding, CascadingRouter
- Functions: __init__, resolve, invoke_with_fallback, is_healthy, mark_healthy, mark_unhealthy, _cost_key
- Imports: __future__, core.error_classification, core.events, core.ledger, core.model_registry, dataclasses, time, typing

### `core\context_packer.py`
- Classes: FileEntry, ContextManifest, ContextPacker
- Functions: to_dict, __init__, pack, _should_exclude, _relevance_score, _detect_language
- Imports: __future__, core.redaction, core.repo.scanner, core.tool_protocol, dataclasses, json, pathlib, typing

### `core\errors.py`
- Classes: AIteamError, ConfigError, ProviderError, RepoInspectionError, ToolSafetyError, PlanningError, ExecutionError, PatchApplicationError, VerificationError, ResumeError, IntegrationError
- Functions: none
- Imports: none

### `core\error_classification.py`
- Classes: ErrorCategory
- Functions: classify_error, should_retry, max_retries_for, backoff_for, should_halt, error_summary
- Imports: __future__, enum, socket, ssl, typing

### `core\events.py`
- Classes: EventType, Event
- Functions: to_dict, to_json, compute_hash, from_dict, from_json, create
- Imports: __future__, dataclasses, datetime, enum, hashlib, json, typing, uuid

### `core\json_repair.py`
- Classes: none
- Functions: extract_json_object, repair_json_text
- Imports: __future__, json

### `core\ledger.py`
- Classes: RunLedger
- Functions: slugify, create, _sanitize_value, write_json, write_text, append_jsonl, emit_event, read_ledger, verify_chain, _read_last_hash, _append_to_ledger, _append_hash, _restore_sequence_from_ledger, _update_index, _persist_index, _load_index, query_index, events_after, save_checkpoint, load_last_checkpoint, list_checkpoints
- Imports: __future__, core.events, dataclasses, datetime, hashlib, json, pathlib, re, threading, typing

### `core\logging.py`
- Classes: none
- Functions: configure_logging
- Imports: logging

### `core\model_registry.py`
- Classes: ProviderDescriptor, ModelDescriptor, ModelRegistry
- Functions: __init__, from_team_config, list_models, resolve_model, create_provider
- Imports: __future__, config.config, dataclasses, importlib, providers.base

### `core\patching.py`
- Classes: AppliedFileChange, PatchApplyResult, PatchApplier
- Functions: __init__, validate_relative_path, apply_changes, rollback, _render_after_text, _normalize_relative, _normalize_input_path, _build_diff
- Imports: __future__, core.errors, difflib, pathlib, pydantic, typing

### `core\policies.py`
- Classes: CommandPolicy
- Functions: classify_command, can_auto_run
- Imports: __future__, enum

### `core\policy_engine.py`
- Classes: DecisionType, PolicyDecision, PolicyConfig, PolicyEngine
- Functions: __init__, evaluate, _emit_policy_event, _check_budget, _is_sensitive
- Imports: __future__, core.events, core.ledger, core.redaction, core.tool_protocol, dataclasses, enum, fnmatch, typing

### `core\privacy_enforcer.py`
- Classes: PrivacyMode, PrivacyEnforcer
- Functions: evaluate, redact_params, _is_sensitive
- Imports: __future__, core.redaction, core.tool_protocol, dataclasses, enum, fnmatch, typing

### `core\public_api.py`
- Classes: none
- Functions: none
- Imports: __future__, core.agent_protocol, core.approval_workflow, core.artifact_store, core.capability_registry, core.cascading_router, core.context_packer, core.error_classification, core.errors, core.events, core.json_repair, core.ledger, core.model_registry, core.patching, core.policies, core.policy_engine, core.privacy_enforcer, core.redaction, core.replay_engine, core.repo.context_pack

### `core\redaction.py`
- Classes: none
- Functions: _hash_secret, redact_text, redact_dict, replacer
- Imports: __future__, hashlib, re

### `core\replay_engine.py`
- Classes: RunState, ReplayEngine
- Functions: replay, _apply_state_transition
- Imports: __future__, core.events, dataclasses, typing, workflows.base

### `core\resume.py`
- Classes: ResumeOrchestrator
- Functions: list_runs, load_run, load_final_report, __init__, resume
- Imports: __future__, core.errors, core.ledger, core.replay_engine, core.workflow_runner, json, pathlib, typing, workflows.base

### `core\retry_engine.py`
- Classes: RetryExhaustedError, RetryEngine
- Functions: __init__, __init__, execute, execute_with_budget, _with_budget, wrapper
- Imports: __future__, core.error_classification, core.events, core.ledger, functools, time, typing

### `core\run_executor.py`
- Classes: RunStatus, RunRecord, RunExecutor
- Functions: __new__, reset_instance, submit, get, list_runs, subscribe, unsubscribe, _notify, log, _run
- Imports: __future__, agents.self_improving.hooks, dataclasses, enum, logging, monitoring.metrics, pathlib, threading, time, typing, uuid

### `core\schemas.py`
- Classes: WorkflowStepStatus, AgentMessage, ToolCall, ToolResult, ArtifactRef, PolicyDecision, CapabilityDescriptor, WorkflowStep, WorkflowRun
- Functions: none
- Imports: __future__, enum, pydantic

### `core\schemas_runtime.py`
- Classes: TaskType, UserTask, RepoSnapshotRef, ContextPackRef, AcceptanceCriterion, RiskAssessment, WorkOrder, TaskNode, TaskGraph, AgentMessage, AgentResult, FileChange, TestSuggestion, PatchPlan, VerificationReport, ImplementationPlan
- Functions: none
- Imports: __future__, config.config, enum, pydantic

### `core\state_machine.py`
- Classes: RuntimeState, RuntimeStateMachine
- Functions: __init__, transition, _record
- Imports: __future__, core.errors, core.ledger, enum, typing

### `core\step_budget.py`
- Classes: BudgetSnapshot, BudgetLimits, BudgetExceededError, StepBudgetEnforcer
- Functions: to_dict, to_dict, __init__, __init__, record_tokens, record_tool_call, record_agent_invocation, record_time, check_budget, _check_and_emit, snapshot
- Imports: __future__, core.events, core.ledger, dataclasses, time, typing

### `core\tool_protocol.py`
- Classes: RiskLevel, ParamSchema, ReturnSchema, ToolExample, ToolSchema, ToolBudget, ToolContext, ToolResult, ToolProtocol, BaseTool, AsyncToolProtocol, AsyncBaseTool, ToolRegistry
- Functions: path_allowed, command_allowed, tool_id, schema, risk_level, invoke, __init__, tool_id, schema, risk_level, invoke, validate_params, tool_id, schema, risk_level, ainvoke, __init__, tool_id, schema, risk_level, ainvoke, validate_params, __init__, register, get, get_async, list_tools, discover_by_prefix
- Imports: __future__, abc, dataclasses, enum, pathlib, typing

### `core\workflow_runner.py`
- Classes: WorkflowRunner
- Functions: __init__, run, _run_sequential_group, _run_parallel_group, _run_step, _eval_condition, _execute
- Imports: __future__, concurrent.futures, core.error_classification, core.events, core.ledger, core.replay_engine, core.retry_engine, core.step_budget, memory.tiers.working, pathlib, typing, workflows.base

### `core\__init__.py`
- Classes: none
- Functions: none
- Imports: none

### `core\__main__.py`
- Classes: none
- Functions: none
- Imports: interfaces.cli.cli

### `devtest\project_overview.py`
- Classes: State
- Functions: scan_repo, extract_python_structure, write_overview
- Imports: __future__, ast, langgraph.graph, pathlib, typing

### `federation\protocol.py`
- Classes: DiscoveryRequest, CapabilityAdvertisement, TaskDelegation, ResultRelay, FederationProtocol
- Functions: to_json, from_json, to_json, from_json, to_json, from_json, to_json, from_json, __init__, is_trusted, trust, untrust, fingerprint_public_key
- Imports: __future__, dataclasses, hashlib, typing

### `federation\transport.py`
- Classes: PeerInfo, DiscoverRequest, DelegateRequest, RelayRequest, FederationClient
- Functions: create_federation_app, discover, list_peers, delegate_task, relay_result, __init__, _request, discover, delegate, relay
- Imports: __future__, fastapi, federation.protocol, logging, pydantic, requests, typing

### `federation\__init__.py`
- Classes: none
- Functions: none
- Imports: __future__, federation.protocol, federation.transport

### `marketplace\manager.py`
- Classes: PluginManager
- Functions: __init__, discover, load, unload, list_loaded, get
- Imports: __future__, importlib.util, marketplace.manifest, marketplace.sandbox, pathlib, sys, typing

### `marketplace\manifest.py`
- Classes: PluginManifest
- Functions: to_json, from_json, from_file, validate, compute_signature
- Imports: __future__, dataclasses, hashlib, json, pathlib, typing

### `marketplace\sandbox.py`
- Classes: PluginSandboxError, Sandbox
- Functions: __init__, run, call
- Imports: __future__, contextlib, core.tool_protocol, inspect, signal, typing

### `marketplace\__init__.py`
- Classes: none
- Functions: none
- Imports: __future__, marketplace.manager, marketplace.manifest

### `memory\brain.py`
- Classes: Brain
- Functions: __init__, _validate_scope, perceive, remember, recent, learn, relate, _extract_concepts, summarize
- Imports: __future__, memory.bus, memory.embeddings, memory.episodic, memory.semantic, pathlib, typing

### `memory\bus.py`
- Classes: MemoryBus
- Functions: __new__, __init__, _get_backend, exclusive, shared, read, write, list_keys, search
- Imports: __future__, contextlib, filelock, memory.backends.base, memory.backends.jsonl, memory.backends.sqlite, memory.backends.vector, pathlib, threading, typing

### `memory\embeddings.py`
- Classes: EmbeddingEngine
- Functions: get_engine, __init__, _tokenize, _get_projection, encode, similarity
- Imports: __future__, hashlib, math, numpy, re, typing

### `memory\episodic.py`
- Classes: Episode, EpisodicMemory
- Functions: to_dict, from_dict, __init__, _ensure_table, _enable_wal, record, _compute_importance, _insert, _enforce_cap, _row_to_episode, recall, recent, count
- Imports: __future__, dataclasses, datetime, json, memory.embeddings, pathlib, sqlite3, typing, uuid

### `memory\registry.py`
- Classes: MemoryRegistry
- Functions: get_default_registry, __init__, get, register, list_backends, read, write, search
- Imports: __future__, memory.backends.base, memory.backends.jsonl, memory.backends.sqlite, memory.backends.vector, pathlib, typing

### `memory\semantic.py`
- Classes: Concept, SemanticMemory
- Functions: to_dict, from_dict, __init__, _ensure_table, _enable_wal, learn, _enforce_cap, relate, query, get, list_all, count, _row_to_concept
- Imports: __future__, dataclasses, json, memory.embeddings, pathlib, sqlite3, typing

### `memory\__init__.py`
- Classes: none
- Functions: none
- Imports: core.capability_registry, memory.backends.base, memory.backends.jsonl, memory.backends.sqlite, memory.backends.vector, memory.brain, memory.bus, memory.embeddings, memory.episodic, memory.registry, memory.semantic, memory.tiers.global_, memory.tiers.working

### `monitoring\health.py`
- Classes: HealthStatus, HealthReporter
- Functions: __init__, check_disk_space, check_memory, check_providers, full_report
- Imports: __future__, dataclasses, pathlib, psutil, shutil, typing

### `monitoring\metrics.py`
- Classes: RunMetrics, MetricsCollector
- Functions: __init__, start_run, end_run, record_tool_call, record_error, record_tokens, get_run_metrics, get_prometheus_metrics
- Imports: __future__, dataclasses, time, typing

### `monitoring\__init__.py`
- Classes: none
- Functions: none
- Imports: __future__, monitoring.health, monitoring.metrics

### `multimodal\claude_vision.py`
- Classes: ClaudeVisionProcessor
- Functions: __init__, _call, describe_image, extract_text_from_image
- Imports: __future__, multimodal.protocol, os, requests, typing

### `multimodal\image.py`
- Classes: StubMultimodalProcessor, ImageTool
- Functions: _resolve_processor, describe_image, extract_text_from_image, __init__, _get_processor, invoke
- Imports: __future__, core.tool_protocol, logging, multimodal.claude_vision, multimodal.openai_vision, multimodal.protocol, os, typing

### `multimodal\openai_vision.py`
- Classes: OpenAIVisionProcessor
- Functions: __init__, describe_image, extract_text_from_image
- Imports: __future__, multimodal.protocol, openai, os, typing

### `multimodal\protocol.py`
- Classes: MultimodalProcessor
- Functions: describe_image, extract_text_from_image
- Imports: __future__, abc, typing

### `multimodal\__init__.py`
- Classes: none
- Functions: none
- Imports: __future__, multimodal.image, multimodal.protocol

### `presets\base.py`
- Classes: Question, Preset, PresetRegistry
- Functions: run, __init__, register, list, get, ids
- Imports: __future__, core.capability_registry, dataclasses, typing

### `presets\codebase_assistant.py`
- Classes: CodebaseAssistantPreset
- Functions: __init__, run
- Imports: __future__, presets.base, typing, workflows.coding.runtime

### `presets\command_assistant.py`
- Classes: CommandAssistantPreset
- Functions: __init__, run
- Imports: __future__, presets.base, typing, workflows.command_assistant.runtime

### `presets\docs_maintainer.py`
- Classes: DocsMaintainerPreset
- Functions: __init__, run
- Imports: __future__, presets.base, typing, workflows.docs_maintenance.runtime

### `presets\file_organizer.py`
- Classes: FileOrganizerPreset
- Functions: __init__, run
- Imports: __future__, presets.base, typing, workflows.file_organization.runtime

### `presets\github_maintainer.py`
- Classes: GitHubMaintainerPreset
- Functions: __init__, run
- Imports: __future__, pathlib, presets.base, typing, workflows.github_maintenance.runtime

### `presets\local_document_chat.py`
- Classes: LocalDocumentChatPreset
- Functions: __init__, run
- Imports: __future__, presets.base, typing, workflows.documents.runtime

### `presets\research_report.py`
- Classes: ResearchReportPreset
- Functions: __init__, run
- Imports: __future__, presets.base, typing, workflows.research.runtime

### `presets\__init__.py`
- Classes: none
- Functions: none
- Imports: __future__, presets.base, presets.codebase_assistant, presets.command_assistant, presets.docs_maintainer, presets.file_organizer, presets.github_maintainer, presets.local_document_chat, presets.research_report

### `providers\aws_bedrock.py`
- Classes: AWSBedrockProvider
- Functions: invoke
- Imports: __future__, providers.base

### `providers\azure_foundry.py`
- Classes: AzureFoundryProvider
- Functions: normalize_azure_foundry_endpoint, __init__
- Imports: __future__, providers.openai_v1

### `providers\base.py`
- Classes: ModelRequest, ModelResponse, ModelProvider
- Functions: __init__, invoke
- Imports: __future__, abc, config.config, pydantic, typing

### `providers\oci_genai.py`
- Classes: OCIGenAIProvider
- Functions: invoke
- Imports: __future__, providers.base

### `providers\openai_v1.py`
- Classes: OpenAIV1Provider
- Functions: __init__, invoke
- Imports: __future__, core.errors, openai, providers.base, time

### `providers\__init__.py`
- Classes: none
- Functions: create_provider, list_providers, get_provider_metadata
- Imports: __future__, importlib, providers.base, typing

### `scripts\roadmap-check.py`
- Classes: ViolationLevel, Violation, CheckResult, ArchitectureChecker, ViolationReporter
- Functions: main, __init__, check_all, check_law1_no_provider_logic_in_core, check_law1_no_workflow_logic_in_core, check_law1_no_concrete_imports_in_core, _is_subprocess_exempt, check_law7_policy_engine_for_tools, check_phase_lock, check_reserved_not_implemented, check_event_immutability, check_directory_structure, check_import_boundaries, _ignored_literal_lines, console_report, json_report
- Imports: argparse, ast, dataclasses, enum, json, os, pathlib, re, subprocess, sys, typing

### `tests\test_agent_protocol.py`
- Classes: TestAgentMessage, TestAgentRequest, TestAgentResponse, TestAgentContext
- Functions: test_defaults, test_with_metadata, test_frozen, test_defaults, test_with_messages, test_defaults, test_with_data, test_defaults, test_to_dict, test_from_step_context
- Imports: __future__, core.agent_protocol, pathlib, pytest, workflows.base

### `tests\test_api_server.py`
- Classes: TestHealth, TestAuth, TestTools, TestWorkflows, TestPresets, TestMemory, TestModels, TestProviders, TestRuns, TestWorkflowExecution, TestPresetExecution, TestRunStreaming, TestRunWebSocket, TestMetrics, TestOpenAPI
- Functions: client, test_health_no_auth, test_missing_api_key, test_invalid_api_key, test_valid_api_key, test_list_tools, test_tool_schema_has_parameters, test_invoke_tool_not_found, test_invoke_high_risk_blocked, test_invoke_filesystem_read, test_invoke_browser_blocked, test_list_workflows, test_get_workflow_detail, test_get_workflow_not_found, test_list_presets, test_read_missing_key, test_write_and_read, test_list_models, test_list_providers, test_run_not_found, test_run_found, test_execute_workflow_not_found, test_execute_workflow_returns_run_id, test_run_preset_not_found, test_run_preset_returns_run_id, test_stream_run_not_found, test_websocket_run_not_found, test_websocket_receives_status_updates, test_metrics_endpoint, test_openapi_schema, test_docs_endpoint, _slow_task
- Imports: __future__, core.run_executor, fastapi.testclient, interfaces.api_server, interfaces.api_server.auth, pathlib, pytest, starlette.websockets, threading, time, unittest.mock

### `tests\test_approval_workflow.py`
- Classes: TestApprovalRequest, TestApprovalWorkflow, TestApprovalWorkflowWithLedger
- Functions: test_six_field_disclosure, test_params_are_redacted, test_to_dict_round_trip, test_request_creates_pending, test_grant_removes_pending, test_deny_removes_pending, test_grant_unknown_returns_none, test_deny_unknown_returns_none, ledger, test_request_emits_approval_requested, test_grant_emits_approval_granted, test_deny_emits_approval_denied, test_multiple_requests_tracked_independently
- Imports: __future__, core.approval_workflow, core.events, core.ledger, core.policy_engine, core.tool_protocol, pathlib, pytest

### `tests\test_artifact_store.py`
- Classes: TestArtifactStoreCreate, TestArtifactStoreValidation, TestArtifactStoreProducers, TestArtifactStoreList
- Functions: test_create_run_makes_directory, test_create_run_produces_run_json, test_create_run_produces_config_redacted, test_empty_run_is_not_complete, test_fresh_create_run_is_not_complete, test_complete_run, test_invalid_json_detected, test_invalid_jsonl_detected, test_missing_checkpoints_directory, test_produce_context_artifacts, test_produce_plan, test_produce_final_report, test_produce_verification, test_produce_patch, test_list_artifacts, test_run_artifacts_count
- Imports: __future__, core.artifact_store, json, pathlib, pytest

### `tests\test_browser_tool.py`
- Classes: TestBrowserToolSchema, TestBrowserToolPolicy, TestBrowserToolFallbackChain, TestBrowserToolHttpFallback, TestBrowserToolPlaywrightMocked, TestBrowserToolSessions, TestBrowserToolSavePathValidation, TestBrowserToolIntegration
- Functions: test_tool_id, test_risk_level, test_schema_has_required_params, test_network_blocked, test_missing_url_for_navigate, test_missing_operation, test_playwright_available_flag, test_screenshot_requires_playwright, test_click_requires_playwright, test_fill_requires_playwright, test_evaluate_requires_playwright, test_navigate_http_fallback, test_navigate_http_fallback_fetch_failure, test_get_text_http_fallback, test_get_text_http_fallback_with_selector, test_get_text_http_fallback_selector_not_found, test_get_links_http_fallback, test_navigate_transient_playwright, test_get_text_transient_playwright, test_get_text_transient_with_selector, test_get_links_transient_playwright, test_screenshot_transient_base64, test_screenshot_transient_save_to_file, test_click_transient_playwright, test_fill_transient_playwright, test_evaluate_transient_playwright, test_create_session, test_close_session, test_navigate_with_session, test_click_with_session, test_session_not_found, test_save_path_escapes_workspace, test_save_path_inside_workspace, test_none_save_path, test_navigate_httpbin, test_get_text_httpbin, test_get_links_httpbin
- Imports: __future__, core.errors, core.tool_protocol, json, pathlib, pytest, tools.browser, tools.browser.session, unittest.mock

### `tests\test_cascading_router.py`
- Classes: TestModelBinding, TestCascadingRouterResolve, TestCascadingRouterHealth, TestCascadingRouterInvoke
- Functions: _make_registry, test_frozen, test_resolve_single_candidate, test_resolve_no_match_raises, test_resolve_emits_model_selected, test_mark_unhealthy_excludes_from_fallbacks, test_health_ttl_expires, test_invoke_primary_succeeds, test_fallback_on_transient_error, test_non_transient_error_raises_immediately, test_all_models_failed_raises, fn, fn, fn, fn
- Imports: __future__, config.config, core.cascading_router, core.events, core.ledger, core.model_registry, core.tool_protocol, pathlib, pytest

### `tests\test_context_packer.py`
- Classes: DummyTool, TestContextPackerBasic, TestContextPackerWithTools, TestContextPackerWithConfig, TestContextPackerExcludes, TestContextPackerLanguageDetection
- Functions: _make_repo, __init__, invoke, test_packs_bundle_and_manifest, test_redacts_secrets, test_respects_budget, test_readme_prioritized, test_manifest_to_dict, test_includes_tools_section, test_includes_config_section, test_excludes_binary_files, test_excludes_venv, test_detects_python
- Imports: __future__, core.context_packer, core.tool_protocol, pathlib, pytest

### `tests\test_desktop_ui.py`
- Classes: TestDesktopUI
- Functions: test_import, test_pyqt6_import_or_skip, test_tkinter_import, test_server_thread_logic
- Imports: PyQt6, __future__, interfaces.desktop_ui, interfaces.desktop_ui.app, pathlib, pytest, tkinter

### `tests\test_distributed.py`
- Classes: TestProtocolMessages, TestTaskScheduler, TestWorkerPool
- Functions: test_worker_registration_roundtrip, test_task_assignment_roundtrip, test_task_result_roundtrip, test_heartbeat_roundtrip, test_register_worker, test_heartbeat_updates_status, test_submit_and_assign_task, test_no_assignment_for_busy_worker, test_task_retry_on_failure, test_prune_unhealthy_workers, test_capability_based_routing, test_pool_start_stop, test_pool_context_manager, test_pool_submit_default_handler, test_pool_submit_custom_handler, test_pool_submit_error
- Imports: __future__, pytest, time, workflows.distributed, workflows.distributed.protocol, workflows.distributed.scheduler

### `tests\test_distributed_transport.py`
- Classes: TestCoordinatorApp, TestCoordinatorClient
- Functions: test_register_worker, test_heartbeat, test_poll_task_no_task, test_submit_and_poll_task, test_status_endpoint, test_register, test_poll_task_no_task, test_poll_task_with_task, test_submit_result
- Imports: __future__, fastapi.testclient, unittest.mock, workflows.distributed, workflows.distributed.protocol, workflows.distributed.transport

### `tests\test_error_classification.py`
- Classes: TestClassifyError, TestRetryStrategy, TestHaltStrategy, TestRetryConfig, TestErrorSummary, CustomError, MyConnectionError
- Functions: test_connection_error_is_transient, test_timeout_error_is_transient, test_socket_timeout_is_transient, test_ssl_error_is_transient, test_os_error_is_transient, test_permission_error_is_permission, test_file_not_found_is_configuration, test_import_error_is_configuration, test_key_error_is_configuration, test_value_error_is_configuration, test_assertion_error_is_verification, test_memory_error_is_fatal, test_recursion_error_is_fatal, test_not_implemented_is_fatal, test_runtime_error_is_fatal, test_unmapped_exception_is_fatal, test_subclass_inherits_parent, test_should_retry_transient, test_should_retry_recoverable, test_should_retry_verification, test_should_not_retry_configuration, test_should_not_retry_permission, test_should_not_retry_fatal, test_should_halt_configuration, test_should_halt_permission, test_should_halt_fatal, test_should_not_halt_transient, test_should_not_halt_recoverable, test_should_not_halt_verification, test_max_retries_transient, test_max_retries_recoverable, test_max_retries_verification, test_max_retries_default, test_backoff_transient, test_backoff_recoverable, test_backoff_verification, test_backoff_default, test_summary_structure, test_summary_for_transient
- Imports: __future__, core.error_classification, pytest, socket, ssl

### `tests\test_events.py`
- Classes: TestEventType, TestEventSerialization, TestEventHash, TestEventFactory
- Functions: test_all_event_types_are_unique, test_event_type_count, test_event_type_is_str, test_round_trip_dict, test_round_trip_json, test_json_is_deterministic, test_timestamp_is_utc, test_optional_fields_default_to_none, test_hash_is_64_hex_chars, test_hash_deterministic_for_same_data, test_hash_excludes_previous_hash, test_different_sequences_produce_different_hashes, test_different_payloads_produce_different_hashes, test_create_generates_uuid, test_create_increments_sequence, test_create_accepts_all_fields
- Imports: __future__, core.events, datetime, json, pytest, uuid

### `tests\test_federation.py`
- Classes: TestMessageSerialization, TestFederationProtocol
- Functions: test_discovery_request_roundtrip, test_capability_advertisement_roundtrip, test_task_delegation_roundtrip, test_result_relay_roundtrip, test_trust, test_trust_and_untrust, test_fingerprint_public_key
- Imports: __future__, federation

### `tests\test_federation_transport.py`
- Classes: TestFederationApp
- Functions: test_discover, test_list_peers, test_delegate_task, test_relay_result
- Imports: __future__, fastapi.testclient, federation.transport

### `tests\test_import_linting.py`
- Classes: TestImportLinting
- Functions: test_roadmap_check_passes, test_roadmap_check_detects_violation
- Imports: __future__, pathlib, pytest, subprocess, sys

### `tests\test_interface_isolation.py`
- Classes: TestInterfaceIsolation
- Functions: _collect_core_imports, test_no_direct_core_imports, test_public_api_has_all_needed_symbols
- Imports: __future__, ast, core, pathlib, pytest

### `tests\test_ledger_checkpoints.py`
- Classes: TestCheckpoints
- Functions: test_save_checkpoint_creates_file, test_load_last_checkpoint, test_load_last_checkpoint_empty, test_list_checkpoints_sorted, test_checkpoint_includes_timestamp, test_checkpoint_dir_created_on_emit, test_sequence_restored_from_existing_ledger, test_multiple_runs_independent_checkpoints
- Imports: __future__, core.events, core.ledger, json, pathlib, pytest

### `tests\test_ledger_hash.py`
- Classes: TestHashChain, TestLedgerRead
- Functions: test_empty_ledger_verifies, test_single_event_verifies, test_chain_of_events_verifies, test_tampered_event_detected, test_tampered_hash_file_detected, test_first_event_previous_hash_is_none_or_zero, test_subsequent_event_links_previous, test_hash_file_matches_event_hashes, test_read_ledger_returns_events_in_order, test_read_ledger_empty
- Imports: __future__, core.events, core.ledger, pathlib, pytest

### `tests\test_ledger_index.py`
- Classes: TestIndexQuery, TestIndexRebuild
- Functions: test_query_by_event_type, test_query_by_phase, test_query_by_agent_id, test_query_by_tool_id, test_query_by_step_id, test_query_combined_filters, test_query_no_match, test_query_returns_empty_for_empty_ledger, test_query_by_string_event_type, test_index_persists_and_loads, test_index_is_incrementally_updated
- Imports: __future__, core.events, core.ledger, pathlib, pytest

### `tests\test_local_db_tool.py`
- Classes: TestLocalDBToolSchema, TestLocalDBToolSafety, TestLocalDBToolSQLSanitization, TestLocalDBToolQuery, TestLocalDBToolListTables, TestLocalDBToolDescribe, TestLocalDBToolResolvePath
- Functions: _create_test_db, test_tool_id, test_risk_level, test_schema_has_required_params, test_missing_db, test_path_escapes_workspace, test_path_outside_allowed_boundaries, test_empty_sql, test_insert_blocked, test_update_blocked, test_delete_blocked, test_drop_blocked, test_create_blocked, test_select_allowed, test_pragma_allowed, test_explain_allowed, test_with_allowed, test_dangerous_keyword_inside_select_blocked, test_query_returns_columns_and_rows, test_query_limit, test_query_bad_sql, test_list_tables, test_describe_table, test_describe_missing_table_name, test_describe_invalid_table_name, test_resolve_inside_workspace, test_resolve_escapes_workspace
- Imports: __future__, core.errors, core.tool_protocol, pathlib, pytest, sqlite3, tools.local_db

### `tests\test_marketplace.py`
- Classes: TestPluginManifest, TestPluginManager, TestSandbox
- Functions: test_valid_manifest, test_invalid_name, test_missing_version, test_roundtrip_json, test_from_file, test_compute_signature, test_discover_finds_manifests, test_load_success, test_load_missing_manifest, test_load_missing_entry_point, test_unload, test_sandbox_context, test_sandbox_call_success, test_sandbox_call_failure
- Imports: __future__, json, marketplace, marketplace.sandbox, pathlib, pytest

### `tests\test_mcp.py`
- Classes: TestMCPTypeMapping, TestSchemaConversion, TestMCPTool, TestMCPClient, TestMCPConfig
- Functions: test_string_type, test_integer_type, test_number_type, test_boolean_type, test_unknown_type_defaults_to_str, test_convert_simple_schema, test_enum_preserved, _make_tool, test_tool_id_prefixed, test_schema_description, test_risk_level, test_invoke_success, test_invoke_failure, test_connect_command_not_found, test_disconnect_without_connect_is_noop, test_list_tools_and_call_tool_mocked, test_load_config_from_file, test_load_config_env_override, test_default_enabled
- Imports: __future__, core.tool_protocol, json, pathlib, pytest, tools.mcp.client, tools.mcp.config, tools.mcp.pool, tools.mcp.tool_adapter, unittest.mock

### `tests\test_mcp_pool.py`
- Classes: TestMCPConnectionPool
- Functions: test_get_client_creates_new_connection, test_get_client_reuses_active_connection, test_disconnect_all_closes_all, test_context_manager_disconnects_on_exit
- Imports: __future__, pytest, tools.mcp.client, tools.mcp.config, tools.mcp.pool, unittest.mock

### `tests\test_monitoring.py`
- Classes: TestMetricsCollector, TestHealthReporter
- Functions: test_start_and_end_run, test_record_tool_call, test_record_error, test_record_tokens, test_prometheus_export, test_missing_run_returns_none, test_disk_space, test_memory, test_providers, test_full_report
- Imports: __future__, monitoring, time

### `tests\test_multimodal.py`
- Classes: TestStubMultimodalProcessor, TestImageTool
- Functions: test_describe_image, test_extract_text, test_tool_id, test_describe_operation, test_ocr_operation, test_invalid_operation
- Imports: __future__, core.tool_protocol, multimodal, multimodal.image, multimodal.protocol

### `tests\test_policy_audit.py`
- Classes: TestPolicyAuditTrail
- Functions: ledger, context, test_allow_emits_policy_evaluated, test_deny_emits_policy_evaluated, test_ask_emits_policy_evaluated, test_no_ledger_no_events, test_params_redacted_in_payload, test_multiple_evaluations_in_order
- Imports: __future__, core.events, core.ledger, core.policy_engine, core.tool_protocol, pathlib, pytest

### `tests\test_policy_engine.py`
- Classes: TestPolicyEngineDefaults, TestLocalOnlyMode, TestStrictPrivateMode, TestPathBoundaries, TestCommandAllowlistDenylist, TestNetworkRestriction, TestDeleteRestriction, TestBudgetLimit, TestPolicyDecisionImmutability, TestRiskRules
- Functions: test_default_config_allows_none, test_default_config_allows_low, test_default_config_asks_medium, test_default_config_asks_high, test_default_config_denies_critical, test_blocks_http_request, test_blocks_git_push, test_allows_local_tool, test_blocks_env_file, test_blocks_pem_file, test_allows_regular_file, test_denies_outside_allowed_paths, test_allows_inside_allowed_paths, test_denylist_blocks_denied_command, test_allowlist_blocks_unlisted_command, test_allowlist_allows_listed_command, test_blocks_http_when_network_not_allowed, test_allows_http_when_network_allowed, test_asks_when_delete_require_reason, test_denies_when_delete_no_reason, test_denies_when_budget_exceeded, test_allows_when_budget_available, test_frozen_dataclass, test_custom_risk_rules
- Imports: __future__, core.policy_engine, core.tool_protocol, pathlib, pytest

### `tests\test_privacy_enforcer.py`
- Classes: TestPrivacyMode, TestPrivacyEnforcerStandard, TestPrivacyEnforcerLocalOnly, TestPrivacyEnforcerStrictPrivate, TestPrivacyEnforcerEncrypted, TestPrivacyEnforcerRedactParams, TestPrivacyEnforcerCustomPatterns
- Functions: test_standard_is_standard, test_local_only_is_local_only, test_strict_private_is_strict_private, test_encrypted_is_encrypted, test_standard_allows_network_tool, test_standard_allows_any_path, test_standard_no_redaction, test_blocks_http_tool, test_blocks_git_push, test_allows_local_tool, test_blocks_sensitive_path, test_blocks_key_file, test_allows_non_sensitive_path, test_blocks_sensitive_path, test_marks_redacted, test_redacts_secrets, test_custom_pattern_blocks, test_custom_pattern_allows_others
- Imports: __future__, core.privacy_enforcer, core.tool_protocol, pathlib, pytest

### `tests\test_provider_lazy_loading.py`
- Classes: TestProviderLazyLoading
- Functions: test_list_providers_does_not_load_modules, test_get_provider_metadata_does_not_load, test_create_provider_loads_requested_only, test_create_provider_unknown_raises, test_base_classes_eagerly_available, test_all_exports_present
- Imports: __future__, providers, providers.base, pytest, sys

### `tests\test_public_api.py`
- Classes: TestPublicApiExports, TestPublicApiImportSafety, TestPublicApiFile
- Functions: test_all_expected_symbols_exist, test_no_internal_modules_exposed, test_all_in_dunder_all, test_import_does_not_load_providers, test_no_direct_core_imports_in_public_api
- Imports: __future__, ast, core.public_api, importlib, pathlib, pytest, sys

### `tests\test_replay_engine.py`
- Classes: TestReplayEngineEmpty, TestReplayEngineStateTransitions, TestReplayEngineCheckpoints, TestReplayEngineMetadata, TestReplayEngineIdempotency
- Functions: _make_event, test_empty_events, test_completed_step, test_failed_step, test_skipped_step, test_multiple_steps, test_later_event_overwrites, test_checkpoint_sequence_tracked, test_run_initiated_metadata, test_replay_twice_same_result
- Imports: __future__, core.events, core.replay_engine, workflows.base

### `tests\test_resume.py`
- Classes: FakeWorkflow, TestListRuns, TestLoadRun, TestResumeOrchestrator
- Functions: __init__, execute_step, test_empty_when_no_runs, test_lists_run_dirs, test_missing_run_raises, test_resume_missing_run_raises, test_resume_replays_and_skips_completed, test_resume_from_failure_continues
- Imports: __future__, core.events, core.ledger, core.model_registry, core.policy_engine, core.resume, core.tool_protocol, core.workflow_runner, pathlib, pytest, workflows.base

### `tests\test_retry_engine.py`
- Classes: TestRetryEngineExecute, TestRetryEngineWithLedger, TestRetryEngineWithBudget
- Functions: test_success_no_retry, test_retry_then_success, test_retry_exhausted, test_no_retry_for_fatal, test_no_retry_for_configuration, test_explicit_error_category_override, test_retry_attempts_emitted, test_retry_exhausted_emitted, test_budget_checker_blocks, test_budget_checker_halts, flaky, always_fails, fatal, bad_config, flaky, flaky, always_fails, flaky, checker, never_runs, checker
- Imports: __future__, core.error_classification, core.events, core.ledger, core.retry_engine, pathlib, pytest, typing, unittest.mock

### `tests\test_run_executor.py`
- Classes: TestRunExecutor
- Functions: test_submit_returns_run_id, test_get_returns_record, test_run_completes, test_run_failure, _fail
- Imports: __future__, core.run_executor, time

### `tests\test_self_improving.py`
- Classes: TestFeedbackLoop, TestPromptEvolutionStrategy, TestParameterTuningStrategy, TestToolSelectionStrategy
- Functions: test_capture_and_summarize, test_empty_summarize, test_to_memory, test_no_change_when_successful, test_appends_guidance_on_failures, test_increases_timeout, test_no_change_when_low_timeout_rate, test_increases_score_on_success, test_decreases_score_on_failure, test_clamps_to_bounds
- Imports: __future__, agents.self_improving, agents.self_improving.strategies

### `tests\test_step_budget.py`
- Classes: TestBudgetSnapshot, TestBudgetLimits, TestCheckBudget, TestBudgetEvents, TestBudgetSnapshotMethod
- Functions: test_default_values, test_to_dict, test_defaults_are_none, test_to_dict, test_within_budget, test_exceed_tokens, test_exceed_tool_calls, test_exceed_agent_invocations, test_no_limits_no_enforcement, test_budget_checked_emitted, test_budget_exceeded_emitted, test_record_events_emitted, test_snapshot_reflects_state
- Imports: __future__, core.events, core.ledger, core.step_budget, pathlib, pytest

### `tests\test_tool_protocol.py`
- Classes: DummySyncTool, DummyAsyncTool, TestAsyncBaseTool, TestToolRegistryMixed, TestAsyncToolProtocol, TestAsyncMCPTool, TestAsyncBrowserTool, Incomplete
- Functions: _run_async, __init__, invoke, __init__, ainvoke, test_cannot_instantiate_abstract, test_validate_params_sync_on_async_tool, test_register_and_get_sync_tool, test_register_and_get_async_tool, test_get_async_asserts_type, test_mixed_list_tools, test_discover_by_prefix_mixed, test_isinstance_check, test_ainvoke_delegates_to_thread, test_ainvoke_create_session, test_ainvoke_network_denied, __init__
- Imports: __future__, asyncio, concurrent.futures, core.tool_protocol, pytest, tools.browser, tools.mcp.tool_adapter, typing, unittest.mock

### `tests\test_web_ui.py`
- Classes: TestHealth, TestDashboard, TestTools, TestWorkflows, TestPresets, TestRunWebSocket, TestMemory
- Functions: client, test_health_ok, test_root_returns_html, test_list_tools, test_list_tools_have_risk_levels, test_invoke_tool_not_found, test_invoke_high_risk_tool_blocked, test_invoke_filesystem_read, test_invoke_filesystem_stat, test_list_workflows, test_list_presets, test_websocket_run_not_found, test_websocket_receives_status_updates, test_read_missing_key, test_write_and_read, _slow_task
- Imports: __future__, core.run_executor, fastapi.testclient, interfaces.web_ui, pathlib, pytest, starlette.websockets, threading, time

### `tests\test_workflow_isolation.py`
- Classes: TestWorkflowIsolation
- Functions: _workflow_files, _collect_core_imports, test_workflow_facing_modules_use_public_api
- Imports: __future__, ast, pathlib

### `tests\test_workflow_runner.py`
- Classes: FakeWorkflow, TestWorkflowRunnerBasic, TestWorkflowRunnerBudget, TestWorkflowRunnerLifecycle
- Functions: _make_registry, __init__, execute_step, on_run_complete, test_sequential_execution, test_event_emission, test_condition_skip, test_condition_requires_success, test_halt_on_failure, test_run_failed_event_on_failure, test_retry_success, test_retry_exhausted, test_workspace_isolation, test_no_workspace_isolation, test_working_memory_flushed, test_budget_enforced, test_budget_event_emitted, test_on_step_complete_called, test_dag_none_raises, flaky, always_fails, capture, capture
- Imports: __future__, core.events, core.ledger, core.model_registry, core.policy_engine, core.step_budget, core.tool_protocol, core.workflow_runner, pathlib, pytest, typing, unittest.mock, workflows.base

### `tests\test_workflow_runner_parallel.py`
- Classes: FakeWorkflow, TestParallelExecution
- Functions: _make_registry, __init__, execute_step, on_run_complete, test_parallel_steps_run_concurrently, test_mixed_parallel_and_sequential, test_parallel_with_dependencies, test_single_step_not_parallel, test_parallel_safe_false_runs_sequential, test_parallel_group_with_failure, test_events_emitted_for_parallel
- Imports: __future__, core.events, core.ledger, core.model_registry, core.policy_engine, core.tool_protocol, core.workflow_runner, pathlib, pytest, threading, time, typing, unittest.mock, workflows.base

### `tools\registry.py`
- Classes: ToolRegistry
- Functions: __init__
- Imports: __future__, pathlib, tools.browser, tools.filesystem, tools.git, tools.local_db, tools.shell, tools.tests

### `tools\tests.py`
- Classes: TestTool
- Functions: __init__, run_safe_command
- Imports: __future__, core.repo.command_detect, tools.shell

### `tools\__init__.py`
- Classes: none
- Functions: none
- Imports: tools.registry

### `workflows\base.py`
- Classes: StepBudget, Step, StepContext, StepResult, AgentRole, ExecutionDAG, Workflow
- Functions: __init__, _validate, _check_cycles, topological_order, parallel_groups, __init__, execute_step, verify, on_step_complete, on_run_complete, build_context, generate_report, run, _eval_condition, model_registry, tool_registry, policy_engine, ledger, ledger, visit
- Imports: __future__, abc, core.ledger, core.model_registry, core.policy_engine, core.schemas, core.tool_protocol, core.workflow_runner, dataclasses, memory.tiers.working, pathlib, pydantic, typing

### `workflows\registry.py`
- Classes: none
- Functions: register_builtin_workflows
- Imports: __future__, core.public_api, workflows.command_assistant.workflows.command_assistant, workflows.docs_maintenance.workflows.docs_maintenance, workflows.documents.workflows.documents, workflows.file_organization.workflows.file_organization, workflows.github_maintenance.workflows.github_maintenance, workflows.research.workflows.research

### `Agent-Team\ai_team\__init__.py`
- Classes: none
- Functions: none
- Imports: none

### `Agent-Team\tests\test_command_detect.py`
- Classes: none
- Functions: test_detect_commands_for_node_and_python
- Imports: ai_team.repo.command_detect, json

### `Agent-Team\tests\test_config.py`
- Classes: none
- Functions: test_redact_secret, test_load_team_config_openai_compatible_registry, test_load_team_config_grok_as_config_only, test_missing_api_key_env_var_fails, test_config_dump_redaction, test_legacy_grok_config_includes_default_capabilities
- Imports: ai_team.config, ai_team.errors, pytest

### `Agent-Team\tests\test_fix_loop.py`
- Classes: none
- Functions: test_build_fix_work_order_includes_verifier_findings
- Imports: ai_team.runtime, ai_team.schemas

### `Agent-Team\tests\test_json_repair.py`
- Classes: none
- Functions: test_extract_json_object_from_wrapped_text, test_repair_json_text_fails_without_json
- Imports: ai_team.json_repair, pytest

### `Agent-Team\tests\test_ledger_paths.py`
- Classes: none
- Functions: test_ledger_scrubs_absolute_repo_paths
- Imports: ai_team.ledger, json

### `Agent-Team\tests\test_model_registry.py`
- Classes: none
- Functions: _seed_env, test_registry_resolves_workflow_roles, test_registry_rejects_unknown_capability, test_registry_uses_models_json_override
- Imports: ai_team.config, ai_team.core.model_registry, json, pytest

### `Agent-Team\tests\test_patching.py`
- Classes: none
- Functions: test_patch_path_validation_blocks_repo_escape, test_patch_apply_rejects_out_of_scope_file
- Imports: ai_team.errors, ai_team.patching, pytest

### `Agent-Team\tests\test_planning_agent.py`
- Classes: FakeProvider
- Functions: _config, test_base_agent_repairs_invalid_json_once, test_base_agent_fails_after_invalid_repair, __init__, invoke
- Imports: ai_team.agents.base, ai_team.config, ai_team.providers.base, ai_team.schemas, json, pathlib, pytest

### `Agent-Team\tests\test_policies.py`
- Classes: none
- Functions: test_command_policy_classification
- Imports: ai_team.policies

### `Agent-Team\tests\test_providers.py`
- Classes: none
- Functions: test_normalize_azure_foundry_endpoint
- Imports: ai_team.providers.azure_foundry

### `Agent-Team\tests\test_redaction.py`
- Classes: none
- Functions: test_redact_text_masks_secret_patterns, test_is_secret_file_detects_secret_names
- Imports: ai_team.repo.redaction, pathlib

### `Agent-Team\tests\test_resume_report.py`
- Classes: none
- Functions: test_resume_and_report_loading
- Imports: ai_team.reports.final_report, ai_team.resume, json

### `Agent-Team\tests\test_run_runtime.py`
- Classes: DummyGit, DummyRegistry
- Functions: test_run_task_blocks_dirty_repo_without_flag, status, __init__
- Imports: ai_team.errors, ai_team.runtime, pathlib, pytest

### `Agent-Team\tests\test_schemas.py`
- Classes: none
- Functions: test_implementation_plan_requires_task_graph
- Imports: ai_team.schemas, pytest

### `Agent-Team\tests\test_state_machine.py`
- Classes: none
- Functions: test_state_machine_happy_path, test_state_machine_rejects_invalid_transition
- Imports: ai_team.errors, ai_team.state_machine, pytest

### `Agent-Team\tests\test_tools.py`
- Classes: none
- Functions: test_repo_sandbox_blocks_escape, test_shell_tool_blocks_install_and_destructive
- Imports: ai_team.tools.filesystem, ai_team.tools.shell, pytest

### `Agent-Team\tests\test_verifier_schema.py`
- Classes: none
- Functions: test_verification_report_accepts_camel_case
- Imports: ai_team.schemas

### `Agent-Team\tests\test_workflow_base.py`
- Classes: DummyProvider, DummyModel, DummyRegistry
- Functions: test_build_agent_uses_registry_provider_signature, invoke, __init__, __init__, resolve_model, create_provider
- Imports: ai_team.config, ai_team.providers.base, ai_team.schemas, ai_team.workflows.base, pathlib

### `agents\self_improving\feedback_loop.py`
- Classes: FeedbackRecord, FeedbackLoop
- Functions: __init__, capture, summarize, to_memory
- Imports: __future__, dataclasses, typing

### `agents\self_improving\hooks.py`
- Classes: SelfImprovingHook
- Functions: __init__, on_run_complete, get_state
- Imports: __future__, agents.self_improving.feedback_loop, agents.self_improving.strategies, logging, typing

### `agents\self_improving\strategies.py`
- Classes: ImprovementStrategy, PromptEvolutionStrategy, ParameterTuningStrategy, ToolSelectionStrategy
- Functions: apply, apply, apply, apply
- Imports: __future__, abc, typing

### `agents\self_improving\__init__.py`
- Classes: none
- Functions: none
- Imports: __future__, agents.self_improving.feedback_loop, agents.self_improving.strategies

### `core\repo\command_detect.py`
- Classes: DetectedCommand
- Functions: detect_commands
- Imports: __future__, json, pathlib, pydantic

### `core\repo\context_pack.py`
- Classes: none
- Functions: build_context_pack
- Imports: __future__, core.redaction, core.repo.scanner, pathlib

### `core\repo\language_detect.py`
- Classes: none
- Functions: detect_languages
- Imports: __future__, collections.abc, pathlib

### `core\repo\redaction.py`
- Classes: none
- Functions: is_secret_file, redact_text, safe_text_excerpt
- Imports: __future__, pathlib, re

### `core\repo\scanner.py`
- Classes: RepoFile, RepoDocument, GitSnapshot, RepoScanResult
- Functions: _should_exclude, _collect_files, _git_snapshot, _read_candidate_docs, inspect_repository
- Imports: __future__, core.repo.command_detect, core.repo.language_detect, core.repo.redaction, pathlib, pydantic, subprocess, typing

### `core\repo\__init__.py`
- Classes: none
- Functions: none
- Imports: core.repo.context_pack, core.repo.scanner

### `extracted\scripts\roadmap-check.py`
- Classes: ViolationLevel, Violation, CheckResult, ArchitectureChecker, ViolationReporter
- Functions: main, __init__, check_all, check_law1_no_provider_logic_in_core, check_law1_no_workflow_logic_in_core, check_law1_no_concrete_imports_in_core, check_law7_policy_engine_for_tools, check_phase_lock, check_reserved_not_implemented, check_event_immutability, check_directory_structure, console_report, json_report
- Imports: argparse, ast, dataclasses, enum, json, os, pathlib, re, subprocess, sys, typing

### `interfaces\api_server\app.py`
- Classes: HealthResponse, ToolSchemaItem, ToolInvokeRequest, ToolInvokeResponse, WorkflowListItem, WorkflowDetail, WorkflowExecuteRequest, PresetListItem, PresetRunRequest, ExecuteResponse, MemoryReadResponse, MemoryWriteRequest, MemoryWriteResponse, ModelListItem, ProviderListItem, RunStatusResponse
- Functions: create_api_app, log_requests, _find_tool, _import_workflows, _tool_schema_to_dict, _check_provider_health, health, list_tools, invoke_tool, list_workflows, get_workflow, execute_workflow, list_presets, run_preset, read_memory, write_memory, list_models, list_providers, get_run_status, stream_run_status, metrics, websocket_run_status, _run, _event_generator, on_update
- Imports: __future__, asyncio, core.public_api, fastapi, fastapi.middleware.cors, fastapi.responses, importlib, interfaces.api_server.auth, interfaces.api_server.rate_limit, json, logging, memory.bus, monitoring.metrics, pathlib, presets, pydantic, time, tools.registry, typing, workflows.registry

### `interfaces\api_server\auth.py`
- Classes: none
- Functions: _load_keys, verify_api_key, generate_api_key
- Imports: __future__, fastapi, fastapi.security, os, secrets, typing

### `interfaces\api_server\rate_limit.py`
- Classes: _RateLimitEntry, RateLimiter
- Functions: __init__, is_allowed, check
- Imports: __future__, dataclasses, fastapi, time, typing

### `interfaces\api_server\__init__.py`
- Classes: none
- Functions: none
- Imports: __future__, interfaces.api_server.app

### `interfaces\cli\cli.py`
- Classes: none
- Functions: config_dump, ping_models, inspect, plan, run, list_runs_cmd, report, resume, list_presets_cmd, start_preset, guided, memory_cmd, doctor_cmd, mcp_list_cmd, mcp_call_cmd, main
- Imports: __future__, config.config, core.public_api, importlib.util, interfaces.guided_tui.app, json, memory.tiers.global_, os, pathlib, platform, presets, providers.base, rich.console, rich.table, subprocess, sys, tools.mcp.client, tools.mcp.config, typer, typing

### `interfaces\desktop_ui\app.py`
- Classes: none
- Functions: _run_server, _run_pyqt6, _run_tkinter, run_desktop_app, open_browser
- Imports: PyQt6, PyQt6.QtCore, PyQt6.QtWebEngineWidgets, PyQt6.QtWidgets, __future__, interfaces.web_ui, pathlib, sys, threading, tkinter, typing, uvicorn, webbrowser

### `interfaces\desktop_ui\__init__.py`
- Classes: none
- Functions: none
- Imports: __future__, interfaces.desktop_ui.app

### `interfaces\guided_tui\app.py`
- Classes: none
- Functions: _questions_to_dicts, run_guided_tui
- Imports: __future__, interfaces.guided_tui.picker, interfaces.guided_tui.questionnaire, interfaces.guided_tui.render, presets, presets.base, rich.console, typing

### `interfaces\guided_tui\picker.py`
- Classes: none
- Functions: pick_preset
- Imports: __future__, interfaces.guided_tui.render, rich.console, typing

### `interfaces\guided_tui\questionnaire.py`
- Classes: none
- Functions: run_questionnaire, _ask_question, _parse_text, _parse_choice, _parse_boolean, _parse_path
- Imports: __future__, interfaces.guided_tui.render, os, pathlib, rich.console, typing

### `interfaces\guided_tui\render.py`
- Classes: none
- Functions: print_header, print_subheader, print_info, print_success, print_error, print_warning, print_panel, build_preset_table, build_summary_table, _get_preset_name, _get_preset_description
- Imports: __future__, rich.console, rich.panel, rich.table, rich.text

### `interfaces\guided_tui\__init__.py`
- Classes: none
- Functions: none
- Imports: __future__, interfaces.guided_tui.app

### `interfaces\web_ui\app.py`
- Classes: HealthResponse, ToolListItem, ToolInvokeRequest, ToolInvokeResponse, WorkflowListItem, PresetListItem, ExecuteRequest, ExecuteResponse, MemoryReadResponse, MemoryWriteRequest, MemoryWriteResponse, RunStatusResponse
- Functions: create_app, _import_workflows, _dashboard_html, root, health, list_tools, invoke_tool, list_workflows, execute_workflow, list_presets, run_preset, get_run_status, stream_run_status, read_memory, write_memory, websocket_run_status, _run, _event_generator, on_update
- Imports: __future__, asyncio, core.public_api, fastapi, fastapi.responses, fastapi.staticfiles, json, memory.bus, pathlib, presets, pydantic, tools.registry, typing, workflows.registry

### `interfaces\web_ui\__init__.py`
- Classes: none
- Functions: none
- Imports: __future__, interfaces.web_ui.app

### `memory\backends\base.py`
- Classes: MemoryBackend
- Functions: __init__, read, write, list_keys, search, _sanitize_key, _scope_dir
- Imports: __future__, abc, pathlib, typing

### `memory\backends\jsonl.py`
- Classes: JsonlBackend
- Functions: read, write, list_keys, search
- Imports: __future__, json, memory.backends.base, pathlib, typing

### `memory\backends\sqlite.py`
- Classes: SqliteBackend
- Functions: __init__, _ensure_table, read, write, list_keys, search
- Imports: __future__, json, memory.backends.base, pathlib, sqlite3, typing

### `memory\backends\vector.py`
- Classes: VectorBackend
- Functions: __init__, _index_path, _load, _save, write, read, list_keys, search
- Imports: __future__, json, memory.backends.base, memory.embeddings, numpy, pathlib, typing

### `memory\backends\__init__.py`
- Classes: none
- Functions: none
- Imports: memory.backends.base, memory.backends.jsonl, memory.backends.sqlite

### `memory\tiers\global_.py`
- Classes: GlobalMemory
- Functions: __init__, _ensure_table, _enable_wal, get_preference, set_preference, record_approval, get_approval_history, record_model_result, get_model_profile
- Imports: __future__, core.redaction, json, pathlib, platformdirs, sqlite3, typing

### `memory\tiers\working.py`
- Classes: WorkingMemory
- Functions: __init__, set, get, append, get_list, snapshot, flush, clear
- Imports: __future__, core.ledger, typing

### `memory\tiers\__init__.py`
- Classes: none
- Functions: none
- Imports: memory.tiers.global_, memory.tiers.working

### `tests\core\test_errors.py`
- Classes: TestErrorHierarchy
- Functions: test_base_is_exception, test_config_error_is_base, test_provider_error_is_base, test_execution_error_is_base, test_planning_error_is_base, test_patch_application_error_is_base, test_verification_error_is_base, test_tool_safety_error_is_base, test_repo_inspection_error_is_base, test_resume_error_is_base, test_error_chaining
- Imports: __future__, core.errors, pytest

### `tests\core\test_ledger.py`
- Classes: TestRunLedger, TestRunLedgerUnified
- Functions: test_create_makes_directory, test_create_makes_jsonl_files, test_write_json, test_write_text, test_append_jsonl, test_sanitize_value_replaces_repo_root, test_sanitize_value_no_repo_root, test_emit_event_creates_ledger_jsonl, test_emit_event_creates_hash_file, test_emit_event_returns_event, test_emit_event_increments_sequence, test_legacy_and_unified_coexist
- Imports: __future__, core.events, core.ledger, json, pathlib, pytest

### `tests\core\test_model_registry.py`
- Classes: TestModelRegistry
- Functions: _make_registry, test_resolve_model_by_capability, test_resolve_model_second_capability, test_resolve_model_not_found, test_resolve_model_wrong_role, test_from_team_config, test_create_provider_unsupported
- Imports: __future__, config.config, core.model_registry, pytest

### `tests\core\test_redaction.py`
- Classes: TestRedactText, TestRedactDict
- Functions: test_api_key_redaction, test_token_redaction, test_password_redaction, test_bearer_token_redaction, test_no_secrets_unchanged, test_aws_key_redaction, test_dict_with_secret, test_nested_dict, test_list_with_secrets, test_no_secrets_preserved
- Imports: __future__, core.redaction, pytest

### `tests\core\test_schemas.py`
- Classes: TestAgentMessage, TestArtifactRef, TestPolicyDecision, TestToolCall, TestToolResult, TestWorkflowStep
- Functions: test_valid_message, test_empty_actor_fails, test_empty_content_fails, test_valid_ref, test_missing_fields_fails, test_allowed, test_denied, test_valid_call, test_success, test_failure, test_default_status, test_status_enum_values
- Imports: __future__, core.schemas, pydantic, pytest

### `tests\memory\test_backends.py`
- Classes: TestJsonlBackend, TestSqliteBackend, TestVectorBackend
- Functions: test_write_and_read, test_read_missing_key_returns_none, test_overwrite_returns_latest, test_scope_isolation, test_list_keys, test_search_finds_matching_value, test_sanitize_key_blocks_dangerous_chars, test_write_and_read, test_read_missing_key_returns_none, test_upsert_overwrites, test_scope_isolation, test_list_keys, test_search_uses_like, test_persists_across_instances, test_write_and_read, test_search_ranking, test_search_returns_scores, test_persists_across_instances, test_empty_search_returns_empty, test_corruption_recovery_skips_bad_lines, test_corruption_recovery_skips_bad_lines_in_search
- Imports: __future__, json, memory.backends.jsonl, memory.backends.sqlite, memory.backends.vector, pytest

### `tests\memory\test_brain.py`
- Classes: TestBrain
- Functions: test_perceive_creates_episode_and_concepts, test_learn_and_remember, test_relate_connects_concepts, test_remember_fuses_episodes_and_concepts, test_summarize_outputs_text, test_persists_across_instances, test_auto_extract_concepts_from_perceive, test_deduplication_merges_high_similarity, test_deduplication_creates_related_for_medium_similarity, test_empty_remember_returns_empty, test_creates_project_scope_file, test_rejects_different_project, test_accepts_same_project_on_reopen
- Imports: __future__, memory.brain, pytest

### `tests\memory\test_bus.py`
- Classes: TestMemoryBus
- Functions: test_singleton_per_repo_root, test_different_repos_get_different_instances, test_write_and_read, test_read_missing_returns_none, test_list_keys, test_search, test_exclusive_lock_is_reentrant, test_shared_lock_allows_concurrent_reads, test_exclusive_blocks_concurrent_writes, test_creates_memory_directory, test_backend_instances_are_reused, test_all_backend_types_accessible, reader, writer
- Imports: __future__, memory.bus, pathlib, pytest, threading, time

### `tests\memory\test_embeddings.py`
- Classes: TestEmbeddingEngine
- Functions: test_encode_produces_normalized_vector, test_encode_empty_text_is_zero_vector, test_similarity_of_identical_text_is_one, test_similarity_of_unrelated_text_is_low, test_similarity_is_symmetric, test_tokenization_filters_short_words, test_get_engine_returns_singleton
- Imports: __future__, memory.embeddings, numpy, pytest

### `tests\memory\test_episodic.py`
- Classes: TestEpisodicMemory
- Functions: test_record_creates_episode, test_recent_returns_latest_first, test_recall_finds_similar_episodes, test_recall_empty_memory_returns_empty, test_persists_across_instances, test_record_without_optional_fields, test_importance_scoring_emotion, test_importance_scoring_outcome_error, test_eviction_respects_importance
- Imports: __future__, memory.episodic, pytest, sqlite3

### `tests\memory\test_registry.py`
- Classes: TestMemoryRegistry, DummyBackend
- Functions: test_default_backends_registered, test_get_backend, test_get_missing_raises, test_register_custom_backend, test_read_write_through_registry, test_search_through_registry, test_default_registry_is_singleton, test_registry_uses_project_subpath, test_different_projects_get_different_registries, read, write, list_keys, search
- Imports: __future__, memory.backends.base, memory.registry, pytest

### `tests\memory\test_semantic.py`
- Classes: TestSemanticMemory
- Functions: test_learn_creates_concept, test_get_retrieves_concept, test_get_missing_returns_none, test_relate_adds_bidirectional_link, test_query_finds_similar_concepts, test_query_empty_returns_empty, test_persists_across_instances, test_learn_overwrites_existing
- Imports: __future__, memory.semantic, pytest

### `tests\memory\test_stress.py`
- Classes: TestCrossProcess, TestStress
- Functions: test_concurrent_writes_no_corruption, test_crash_recovery, test_episodic_recall_performance, test_semantic_query_performance, test_vector_search_performance
- Imports: __future__, memory.backends.vector, memory.brain, memory.embeddings, numpy, pathlib, pytest, subprocess, sys, time

### `tests\memory\test_tiers.py`
- Classes: TestWorkingMemory, TestGlobalMemory
- Functions: test_set_get, test_get_missing_returns_default, test_append_and_get_list, test_snapshot, test_clear, test_flush_without_ledger_is_noop, test_flush_writes_to_ledger, test_get_preference_default, test_set_and_get_preference, test_set_preference_overwrites, test_preference_persists_across_instances, test_preference_stores_complex_value, test_record_approval, test_approval_history_limit, test_record_model_result_new, test_record_model_result_updates, test_get_model_profile_missing, test_wal_mode_enabled, test_preference_redaction
- Imports: __future__, core.ledger, json, memory.tiers.global_, memory.tiers.working, pathlib, pytest, sqlite3

### `tests\smoke\test_cli.py`
- Classes: TestCliCommands
- Functions: test_config_dump_help, test_presets_command, test_memory_help, test_doctor_help, test_guided_help, test_start_help, test_ping_models_help, test_inspect_help, test_plan_help, test_run_help, test_list_runs_help, test_doctor_runs
- Imports: __future__, interfaces.cli.cli, typer.testing

### `tests\smoke\test_presets.py`
- Classes: TestPresetRegistry
- Functions: test_all_presets_registered, test_preset_has_name_and_description, test_preset_has_workflow_id, test_codebase_assistant_preset, test_local_document_chat_preset, test_research_report_preset, test_file_organizer_preset, test_docs_maintainer_preset, test_github_maintainer_preset, test_command_assistant_preset
- Imports: __future__, presets, pytest

### `tests\smoke\test_workflows.py`
- Classes: TestWorkflowImports, TestWorkflowRuntimeImports, TestWorkflowInstantiation
- Functions: _make_model_registry, _config, test_coding_workflow_imports, test_documents_workflow_imports, test_research_workflow_imports, test_file_organization_workflow_imports, test_docs_maintenance_workflow_imports, test_github_maintenance_workflow_imports, test_command_assistant_workflow_imports, test_coding_runtime_imports, test_documents_runtime_imports, test_research_runtime_imports, test_file_organization_runtime_imports, test_docs_maintenance_runtime_imports, test_github_maintenance_runtime_imports, test_command_assistant_runtime_imports, mock_deps, test_documents_workflow_instantiates, test_research_workflow_instantiates, test_file_organization_workflow_instantiates, test_docs_maintenance_workflow_instantiates, test_github_maintenance_workflow_instantiates, test_command_assistant_workflow_instantiates, test_file_organization_no_crash_on_default_config, test_dag_no_cycles
- Imports: __future__, config.config, core.ledger, core.model_registry, core.policy_engine, core.tool_protocol, pathlib, pytest, unittest.mock, workflows.coding.runtime, workflows.coding.workflows.coding, workflows.command_assistant, workflows.command_assistant.runtime, workflows.docs_maintenance, workflows.docs_maintenance.runtime, workflows.documents, workflows.documents.runtime, workflows.file_organization, workflows.file_organization.runtime, workflows.github_maintenance

### `tests\smoke\test_workflow_execution.py`
- Classes: TestResearchWorkflowExecution, TestCommandAssistantWorkflowExecution, TestFileOrganizationWorkflowExecution
- Functions: _make_model_registry, _fake_invoke, mock_deps, _config, test_research_workflow_runs_end_to_end, test_command_assistant_runs_end_to_end, test_file_organization_runs_end_to_end
- Imports: __future__, config.config, core.ledger, core.model_registry, core.policy_engine, core.tool_protocol, json, pathlib, pytest, typing, unittest.mock, workflows.command_assistant, workflows.command_assistant.agents.base, workflows.file_organization, workflows.file_organization.agents.base, workflows.research, workflows.research.agents.base

### `tests\smoke\__init__.py`
- Classes: none
- Functions: none
- Imports: none

### `tools\browser\session.py`
- Classes: BrowserSession, BrowserSessionManager
- Functions: __init__, close, __new__, reset_instance, create_session, get_page, navigate, close_session, close_all
- Imports: __future__, logging, playwright.sync_api, threading, typing, uuid, weakref

### `tools\browser\__init__.py`
- Classes: BrowserTool, AsyncBrowserTool
- Functions: __init__, invoke, _create_session, _close_session, _get_page, _resolve_save_path, _playwright_available, _navigate, _get_text, _get_links, _screenshot, _click, _fill, _evaluate, _navigate_playwright, _fetch_with_requests, _fetch_with_urllib, _fetch, _navigate_http_fallback, _get_text_http_fallback, _get_links_http_fallback, __init__, ainvoke, _create_session_sync, _close_session_sync, _sync_invoke, _async_transient_invoke
- Imports: __future__, asyncio, base64, bs4, core.errors, core.tool_protocol, pathlib, playwright.async_api, playwright.sync_api, re, requests, tools.browser.session, typing, urllib.error, urllib.request

### `tools\filesystem\__init__.py`
- Classes: FilesystemTool
- Functions: __init__, _resolve, invoke, _read, _write, _list, _stat
- Imports: __future__, core.errors, core.tool_protocol, os, pathlib, typing

### `tools\git\github_cli.py`
- Classes: GitHubCliAdapter
- Functions: __init__, available, _run, view_issue, view_pr, view_workflow_run
- Imports: __future__, core.errors, pathlib, shutil, subprocess

### `tools\git\__init__.py`
- Classes: GitTool
- Functions: __init__, _run, invoke, _status, _diff, _diff_patch, _commit, _clone, _push
- Imports: __future__, core.errors, core.tool_protocol, pathlib, subprocess, typing

### `tools\http\__init__.py`
- Classes: HttpTool
- Functions: __init__, invoke
- Imports: __future__, core.errors, core.tool_protocol, json, typing, urllib.request

### `tools\integrations\mcp_client.py`
- Classes: MCPClientAdapter
- Functions: __init__, available, call
- Imports: __future__, pathlib, typing

### `tools\integrations\web_research.py`
- Classes: DuckDuckGoSearchAdapter, UrllibSearchAdapter, WebResearchAdapter
- Functions: __init__, available, search, search, __init__, available, search
- Imports: __future__, duckduckgo_search, pathlib, re, typing, urllib.error, urllib.request

### `tools\integrations\__init__.py`
- Classes: none
- Functions: none
- Imports: tools.git.github_cli, tools.integrations.mcp_client, tools.integrations.web_research

### `tools\local_db\__init__.py`
- Classes: LocalDBTool
- Functions: __init__, invoke, _resolve_db_path, _sanitize_sql, _query, _list_tables, _describe
- Imports: __future__, core.errors, core.tool_protocol, pathlib, sqlite3, typing

### `tools\mcp\client.py`
- Classes: MCPError, MCPClient
- Functions: __init__, _next_id, connect, disconnect, __enter__, __exit__, list_tools, call_tool, _ensure_connected, _send, _read_response
- Imports: __future__, json, logging, subprocess, threading, time, typing

### `tools\mcp\config.py`
- Classes: MCPServerConfig
- Functions: load_mcp_config
- Imports: __future__, dataclasses, json, os, pathlib, typing

### `tools\mcp\pool.py`
- Classes: MCPConnectionPool
- Functions: __init__, get_client, release_client, disconnect, disconnect_all, _disconnect_locked, __enter__, __exit__
- Imports: __future__, logging, threading, tools.mcp.client, tools.mcp.config, typing, weakref

### `tools\mcp\tool_adapter.py`
- Classes: MCPTool, AsyncMCPTool
- Functions: _mcp_type_to_param_type, _convert_schema, __init__, invoke, __init__, ainvoke, _sync_invoke
- Imports: __future__, asyncio, core.tool_protocol, json, logging, tools.mcp.client, tools.mcp.config, tools.mcp.pool, typing

### `tools\mcp\__init__.py`
- Classes: none
- Functions: register_mcp_tools
- Imports: __future__, core.tool_protocol, json, logging, pathlib, tools.mcp.client, tools.mcp.config, tools.mcp.pool, tools.mcp.tool_adapter, typing

### `tools\memory\__init__.py`
- Classes: MemoryTool
- Functions: __init__, _path, invoke
- Imports: __future__, core.tool_protocol, json, pathlib, typing

### `tools\shell\__init__.py`
- Classes: ShellResult, ShellTool
- Functions: __init__, invoke
- Imports: __future__, core.errors, core.policies, core.tool_protocol, pathlib, pydantic, subprocess, typing

### `workflows\coding\adapters.py`
- Classes: none
- Functions: model_resolve, ledger_append, _get_tool_registry, _get_policy_engine, _make_context, tool_invoke, policy_evaluate
- Imports: __future__, core.public_api, pathlib, tools.filesystem, tools.git, tools.http, tools.memory, tools.shell, typing

### `workflows\coding\provider_map.py`
- Classes: none
- Functions: none
- Imports: __future__, core.public_api

### `workflows\coding\runtime.py`
- Classes: PlanningError
- Functions: build_plan_prompt, plan_task, _write_run_command_output, _collect_work_order_context, _basic_verify, _ledger_integrity_check, _build_fix_work_order, _run_verifier, run_task
- Imports: __future__, config.config, core.public_api, json, pathlib, tools.git.github_cli, tools.integrations.mcp_client, tools.integrations.web_research, typing, workflows.coding.adapters, workflows.coding.provider_map, workflows.coding.reports.final_report, workflows.coding.reports.markdown, workflows.coding.workflows.coding

### `workflows\command_assistant\runtime.py`
- Classes: none
- Functions: plan_task, run_task
- Imports: __future__, config.config, core.public_api, json, pathlib, typing, workflows.coding.provider_map, workflows.command_assistant.reports.final_report, workflows.command_assistant.reports.markdown, workflows.command_assistant.workflows.command_assistant

### `workflows\command_assistant\__init__.py`
- Classes: none
- Functions: none
- Imports: workflows.command_assistant.workflows.command_assistant

### `workflows\distributed\pool.py`
- Classes: WorkerPool
- Functions: _execute_task, __init__, register_handler, start, stop, submit, __enter__, __exit__
- Imports: __future__, concurrent.futures, multiprocessing, typing, workflows.distributed.protocol

### `workflows\distributed\protocol.py`
- Classes: WorkerStatus, WorkerRegistration, TaskAssignment, TaskResult, Heartbeat
- Functions: to_json, from_json, to_json, from_json, to_json, from_json, to_json, from_json
- Imports: __future__, dataclasses, enum, typing

### `workflows\distributed\scheduler.py`
- Classes: _WorkerState, TaskScheduler
- Functions: __init__, register_worker, heartbeat, submit_task, next_assignment, complete_task, prune_unhealthy_workers, worker_count, pending_count, completed_count
- Imports: __future__, dataclasses, time, typing, workflows.distributed.protocol

### `workflows\distributed\server.py`
- Classes: RegisterRequest, HeartbeatRequest, TaskSubmitRequest, TaskCompleteRequest
- Functions: create_coordinator_app, register_worker, heartbeat, poll_task, submit_task, complete_task, status
- Imports: __future__, fastapi, pydantic, typing, workflows.distributed.protocol, workflows.distributed.scheduler

### `workflows\distributed\transport.py`
- Classes: CoordinatorClient, RemoteWorker
- Functions: __init__, _request, register, heartbeat, poll_task, submit_result, __init__, register, run, stop
- Imports: __future__, logging, requests, time, typing, workflows.distributed.protocol

### `workflows\distributed\__init__.py`
- Classes: none
- Functions: none
- Imports: __future__, workflows.distributed.pool, workflows.distributed.protocol, workflows.distributed.scheduler, workflows.distributed.server, workflows.distributed.transport

### `workflows\docs_maintenance\runtime.py`
- Classes: none
- Functions: plan_task, run_task
- Imports: __future__, config.config, core.public_api, json, pathlib, typing, workflows.coding.provider_map, workflows.docs_maintenance.reports.final_report, workflows.docs_maintenance.reports.markdown, workflows.docs_maintenance.workflows.docs_maintenance

### `workflows\docs_maintenance\__init__.py`
- Classes: none
- Functions: none
- Imports: workflows.docs_maintenance.workflows.docs_maintenance

### `workflows\documents\provider_map.py`
- Classes: none
- Functions: none
- Imports: __future__, core.public_api

### `workflows\documents\runtime.py`
- Classes: none
- Functions: plan_task, run_task
- Imports: __future__, config.config, core.public_api, pathlib, typing, workflows.documents.provider_map, workflows.documents.reports.final_report, workflows.documents.reports.markdown, workflows.documents.workflows.documents

### `workflows\documents\__init__.py`
- Classes: none
- Functions: none
- Imports: workflows.documents.workflows.documents

### `workflows\file_organization\runtime.py`
- Classes: FileOrganizationError
- Functions: plan_task, run_task, _build_report
- Imports: __future__, config.config, core.public_api, pathlib, typing, workflows.base, workflows.coding.provider_map, workflows.file_organization.agents.proposer, workflows.file_organization.reports.final_report, workflows.file_organization.reports.markdown, workflows.file_organization.workflows.file_organization

### `workflows\file_organization\__init__.py`
- Classes: none
- Functions: none
- Imports: __future__, workflows.file_organization.workflows.file_organization

### `workflows\github_maintenance\runtime.py`
- Classes: none
- Functions: plan_task, run_task
- Imports: __future__, config.config, core.public_api, json, pathlib, typing, workflows.coding.provider_map, workflows.github_maintenance.reports.final_report, workflows.github_maintenance.reports.markdown, workflows.github_maintenance.workflows.github_maintenance

### `workflows\github_maintenance\__init__.py`
- Classes: none
- Functions: none
- Imports: workflows.github_maintenance.workflows.github_maintenance

### `workflows\research\runtime.py`
- Classes: ResearchPlanningError
- Functions: plan_task, run_task
- Imports: __future__, config.config, core.public_api, pathlib, typing, workflows.coding.provider_map, workflows.research.reports.final_report, workflows.research.reports.markdown, workflows.research.workflows.research

### `workflows\research\__init__.py`
- Classes: none
- Functions: none
- Imports: workflows.research.workflows.research

### `workflows\coding\agents\base.py`
- Classes: BaseAgent
- Functions: load_prompt, __init__, run_structured, _invoke, _parse
- Imports: __future__, config.config, core.json_repair, core.schemas_runtime, json, pathlib, providers.base, pydantic, typing

### `workflows\coding\agents\coder.py`
- Classes: CoderAgent
- Functions: build_prompt, run_work_order
- Imports: __future__, core.schemas_runtime, pathlib, workflows.coding.agents.base

### `workflows\coding\agents\orchestrator.py`
- Classes: OrchestratorAgent
- Functions: none
- Imports: __future__, core.schemas_runtime, workflows.coding.agents.base

### `workflows\coding\agents\verifier.py`
- Classes: VerifierAgent
- Functions: build_prompt, run_verification
- Imports: __future__, core.schemas_runtime, pathlib, workflows.coding.agents.base

### `workflows\coding\agents\__init__.py`
- Classes: none
- Functions: none
- Imports: workflows.coding.agents.base, workflows.coding.agents.coder, workflows.coding.agents.orchestrator, workflows.coding.agents.verifier

### `workflows\coding\reports\final_report.py`
- Classes: VerificationRecord, FinalReport
- Functions: none
- Imports: __future__, pydantic

### `workflows\coding\reports\markdown.py`
- Classes: none
- Functions: render_final_report_markdown
- Imports: __future__, workflows.coding.reports.final_report

### `workflows\coding\reports\__init__.py`
- Classes: none
- Functions: none
- Imports: workflows.coding.reports.final_report

### `workflows\coding\workflows\base.py`
- Classes: AgentSpec
- Functions: build_agent
- Imports: __future__, core.public_api, dataclasses, pathlib, pydantic, typing, workflows.coding.agents.base

### `workflows\coding\workflows\coding.py`
- Classes: none
- Functions: _prompt_dir, create_orchestrator_agent, create_coder_agent, create_verifier_agent
- Imports: __future__, core.public_api, pathlib, workflows.coding.agents.base, workflows.coding.agents.coder, workflows.coding.agents.orchestrator, workflows.coding.agents.verifier

### `workflows\coding\workflows\__init__.py`
- Classes: none
- Functions: none
- Imports: none

### `workflows\command_assistant\agents\base.py`
- Classes: BaseAgent
- Functions: load_prompt, __init__, run_structured, _invoke, _parse
- Imports: __future__, config.config, core.json_repair, core.schemas_runtime, json, pathlib, providers.base, pydantic, typing

### `workflows\command_assistant\agents\generator.py`
- Classes: GeneratedCommand, GeneratorAgent
- Functions: run_generate
- Imports: __future__, core.schemas_runtime, pydantic, workflows.command_assistant.agents.base

### `workflows\command_assistant\agents\parser.py`
- Classes: ParsedIntent, ParserAgent
- Functions: run_parse
- Imports: __future__, core.schemas_runtime, pydantic, workflows.command_assistant.agents.base

### `workflows\command_assistant\agents\__init__.py`
- Classes: none
- Functions: none
- Imports: workflows.command_assistant.agents.base, workflows.command_assistant.agents.generator, workflows.command_assistant.agents.parser

### `workflows\command_assistant\reports\final_report.py`
- Classes: CommandRecord, FinalReport
- Functions: none
- Imports: __future__, pydantic

### `workflows\command_assistant\reports\markdown.py`
- Classes: none
- Functions: render_final_report_markdown
- Imports: __future__, workflows.command_assistant.reports.final_report

### `workflows\command_assistant\workflows\command_assistant.py`
- Classes: CommandAssistantWorkflow
- Functions: _prompt_dir, create_parser_agent, create_generator_agent, __init__, execute_step
- Imports: __future__, core.public_api, pathlib, workflows.base, workflows.command_assistant.agents.base, workflows.command_assistant.agents.generator, workflows.command_assistant.agents.parser

### `workflows\docs_maintenance\agents\aligner.py`
- Classes: AlignmentIssue, AlignmentResult, AlignerAgent
- Functions: run_alignment
- Imports: __future__, core.schemas_runtime, pydantic, workflows.docs_maintenance.agents.base

### `workflows\docs_maintenance\agents\base.py`
- Classes: BaseAgent
- Functions: load_prompt, __init__, run_structured, _invoke, _parse
- Imports: __future__, config.config, core.json_repair, core.schemas_runtime, json, pathlib, providers.base, pydantic, typing

### `workflows\docs_maintenance\agents\detector.py`
- Classes: StaleDocItem, DetectionResult, DetectorAgent
- Functions: run_detection
- Imports: __future__, core.schemas_runtime, pydantic, workflows.docs_maintenance.agents.base

### `workflows\docs_maintenance\agents\updater.py`
- Classes: DocUpdate, UpdateResult, UpdaterAgent
- Functions: run_update
- Imports: __future__, core.schemas_runtime, pydantic, workflows.docs_maintenance.agents.base

### `workflows\docs_maintenance\agents\__init__.py`
- Classes: none
- Functions: none
- Imports: workflows.docs_maintenance.agents.aligner, workflows.docs_maintenance.agents.base, workflows.docs_maintenance.agents.detector, workflows.docs_maintenance.agents.updater

### `workflows\docs_maintenance\reports\final_report.py`
- Classes: DocUpdateRecord, FinalReport
- Functions: none
- Imports: __future__, pydantic

### `workflows\docs_maintenance\reports\markdown.py`
- Classes: none
- Functions: render_final_report_markdown
- Imports: __future__, workflows.docs_maintenance.reports.final_report

### `workflows\docs_maintenance\workflows\docs_maintenance.py`
- Classes: DocsMaintenanceWorkflow
- Functions: _prompt_dir, create_detector_agent, create_updater_agent, create_aligner_agent, __init__, execute_step
- Imports: __future__, core.public_api, pathlib, workflows.base, workflows.docs_maintenance.agents.aligner, workflows.docs_maintenance.agents.base, workflows.docs_maintenance.agents.detector, workflows.docs_maintenance.agents.updater

### `workflows\documents\agents\answerer.py`
- Classes: Citation, AnswererOutput, AnswerAgent
- Functions: build_prompt, run_answer
- Imports: __future__, core.schemas_runtime, pydantic, typing, workflows.documents.agents.base

### `workflows\documents\agents\base.py`
- Classes: BaseAgent
- Functions: load_prompt, __init__, run_structured, _invoke, _parse
- Imports: __future__, config.config, core.json_repair, core.schemas_runtime, json, pathlib, providers.base, pydantic, typing

### `workflows\documents\agents\indexer.py`
- Classes: DocumentEntry, IndexerOutput, IndexerAgent
- Functions: build_prompt, run_index
- Imports: __future__, core.schemas_runtime, pathlib, pydantic, workflows.documents.agents.base

### `workflows\documents\agents\retriever.py`
- Classes: RetrievalChunk, RetrieverOutput, RetrieverAgent
- Functions: build_prompt, run_retrieve
- Imports: __future__, core.schemas_runtime, pydantic, workflows.documents.agents.base

### `workflows\documents\agents\__init__.py`
- Classes: none
- Functions: none
- Imports: workflows.documents.agents.answerer, workflows.documents.agents.base, workflows.documents.agents.indexer, workflows.documents.agents.retriever

### `workflows\documents\reports\final_report.py`
- Classes: Citation, DocumentChatReport
- Functions: none
- Imports: __future__, pydantic

### `workflows\documents\reports\markdown.py`
- Classes: none
- Functions: render_document_chat_report_markdown
- Imports: __future__, workflows.documents.reports.final_report

### `workflows\documents\reports\__init__.py`
- Classes: none
- Functions: none
- Imports: workflows.documents.reports.final_report

### `workflows\documents\workflows\documents.py`
- Classes: DocumentsWorkflow
- Functions: _prompt_dir, _collect_text_files, create_indexer_agent, create_retriever_agent, create_answerer_agent, __init__, execute_step, _execute_index, _execute_retrieve, _execute_answer, generate_report
- Imports: __future__, core.public_api, pathlib, typing, workflows.base, workflows.documents.agents.answerer, workflows.documents.agents.base, workflows.documents.agents.indexer, workflows.documents.agents.retriever

### `workflows\documents\workflows\__init__.py`
- Classes: none
- Functions: none
- Imports: none

### `workflows\file_organization\agents\analyzer.py`
- Classes: FileClassification, AnalyzerResult, AnalyzerAgent
- Functions: build_analyze_prompt
- Imports: __future__, pydantic, workflows.file_organization.agents.base

### `workflows\file_organization\agents\applier.py`
- Classes: AppliedMove, ApplierResult, ApplierAgent
- Functions: build_apply_prompt
- Imports: __future__, pathlib, pydantic, workflows.file_organization.agents.base, workflows.file_organization.agents.proposer

### `workflows\file_organization\agents\base.py`
- Classes: BaseAgent
- Functions: load_prompt, __init__, run_structured, _invoke, _parse
- Imports: __future__, config.config, core.json_repair, core.schemas_runtime, json, pathlib, providers.base, pydantic, typing

### `workflows\file_organization\agents\proposer.py`
- Classes: MoveAction, ProposerResult, ProposerAgent
- Functions: build_propose_prompt, build_preview_prompt
- Imports: __future__, pydantic, workflows.file_organization.agents.analyzer, workflows.file_organization.agents.base

### `workflows\file_organization\agents\__init__.py`
- Classes: none
- Functions: none
- Imports: __future__, workflows.file_organization.agents.analyzer, workflows.file_organization.agents.applier, workflows.file_organization.agents.proposer

### `workflows\file_organization\reports\final_report.py`
- Classes: FileMoveRecord, FileOrganizationReport
- Functions: none
- Imports: __future__, pydantic

### `workflows\file_organization\reports\markdown.py`
- Classes: none
- Functions: render_file_organization_markdown
- Imports: __future__, workflows.file_organization.reports.final_report

### `workflows\file_organization\reports\__init__.py`
- Classes: none
- Functions: none
- Imports: workflows.file_organization.reports.final_report

### `workflows\file_organization\workflows\file_organization.py`
- Classes: FileOrganizationWorkflow
- Functions: __init__, _resolve_agent_model, _resolve_any_role, execute_step, _execute_analyze, _execute_propose, _execute_preview, _execute_apply
- Imports: __future__, core.public_api, pathlib, typing, workflows.base, workflows.file_organization.agents.analyzer, workflows.file_organization.agents.applier, workflows.file_organization.agents.base, workflows.file_organization.agents.proposer

### `workflows\file_organization\workflows\__init__.py`
- Classes: none
- Functions: none
- Imports: none

### `workflows\github_maintenance\agents\base.py`
- Classes: BaseAgent
- Functions: load_prompt, __init__, run_structured, _invoke, _parse
- Imports: __future__, config.config, core.json_repair, core.schemas_runtime, json, pathlib, providers.base, pydantic, typing

### `workflows\github_maintenance\agents\drafter.py`
- Classes: DraftResult, DrafterAgent
- Functions: run_draft
- Imports: __future__, core.schemas_runtime, pydantic, workflows.github_maintenance.agents.base

### `workflows\github_maintenance\agents\summarizer.py`
- Classes: IssueSummaryItem, SummaryResult, SummarizerAgent
- Functions: run_summary
- Imports: __future__, core.schemas_runtime, pydantic, workflows.github_maintenance.agents.base

### `workflows\github_maintenance\agents\__init__.py`
- Classes: none
- Functions: none
- Imports: workflows.github_maintenance.agents.base, workflows.github_maintenance.agents.drafter, workflows.github_maintenance.agents.summarizer

### `workflows\github_maintenance\reports\final_report.py`
- Classes: IssueSummaryRecord, FinalReport
- Functions: none
- Imports: __future__, pydantic

### `workflows\github_maintenance\reports\markdown.py`
- Classes: none
- Functions: render_final_report_markdown
- Imports: __future__, workflows.github_maintenance.reports.final_report

### `workflows\github_maintenance\workflows\github_maintenance.py`
- Classes: GitHubMaintenanceWorkflow
- Functions: _prompt_dir, create_summarizer_agent, create_drafter_agent, __init__, execute_step
- Imports: __future__, core.public_api, pathlib, workflows.base, workflows.github_maintenance.agents.base, workflows.github_maintenance.agents.drafter, workflows.github_maintenance.agents.summarizer

### `workflows\research\agents\base.py`
- Classes: BaseAgent
- Functions: load_prompt, __init__, run_structured, _invoke, _parse
- Imports: __future__, config.config, core.json_repair, core.schemas_runtime, json, pathlib, providers.base, pydantic, typing

### `workflows\research\agents\gatherer.py`
- Classes: Source, GatherResult, GathererAgent
- Functions: build_prompt, run_gather
- Imports: __future__, pydantic, workflows.research.agents.base

### `workflows\research\agents\reporter.py`
- Classes: ReporterAgent
- Functions: build_prompt, run_report
- Imports: __future__, workflows.research.agents.base, workflows.research.reports.final_report

### `workflows\research\agents\summarizer.py`
- Classes: SourceSummary, Comparison, SummaryResult, SummarizerAgent
- Functions: build_prompt, run_summarize
- Imports: __future__, pydantic, workflows.research.agents.base

### `workflows\research\agents\__init__.py`
- Classes: none
- Functions: none
- Imports: workflows.research.agents.gatherer, workflows.research.agents.reporter, workflows.research.agents.summarizer

### `workflows\research\reports\final_report.py`
- Classes: Section, ResearchReport
- Functions: none
- Imports: __future__, pydantic

### `workflows\research\reports\markdown.py`
- Classes: none
- Functions: render_research_report_markdown
- Imports: __future__, workflows.research.reports.final_report

### `workflows\research\workflows\research.py`
- Classes: ResearchWorkflow
- Functions: __init__, _prompt_dir, _create_gatherer, _create_summarizer, _create_reporter, execute_step, generate_report
- Imports: __future__, core.public_api, pathlib, typing, workflows.base, workflows.research.agents.base, workflows.research.agents.gatherer, workflows.research.agents.reporter, workflows.research.agents.summarizer, workflows.research.reports.final_report, workflows.research.reports.markdown
