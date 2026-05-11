cd Agent-Team
pytest -q
pytest -q tests/test_config.py tests/test_model_registry.py tests/test_run_runtime.py
pytest -q tests/test_workflow_base.py
pytest -q tests/test_config.py tests/test_model_registry.py tests/test_planning_agent.py tests/test_run_runtime.py tests/test_providers.py tests/test_tools.py
pytest -q tests/test_config.py tests/test_model_registry.py tests/test_planning_agent.py tests/test_run_runtime.py tests/test_fix_loop.py tests/test_state_machine.py tests/test_resume_report.py tests/test_ledger_paths.py tests/test_patching.py tests/test_tools.py tests/test_policies.py tests/test_providers.py tests/test_verifier_schema.py tests/test_schemas.py tests/test_command_detect.py tests/test_json_repair.py tests/test_redaction.py
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode narrow
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode targeted
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode broad
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode full
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode targeted -K registry
powershell -ExecutionPolicy Bypass -File .\devtest\run-devtest.ps1 -Mode full -K "not slow"
powershell -ExecutionPolicy Bypass -File .\devtest\ai_test.ps1
powershell -ExecutionPolicy Bypass -File .\devtest\ai_test.ps1 -AllowMismatchPurpose
python -c "import sys; sys.path.insert(0, '.'); import workflows.research; print('research workflow registered:', [e.id for e in __import__('core.capability_registry', fromlist=['list_workflows']).list_workflows()])"

# documents workflow smoke tests (root project)
cd ..
python -c "from workflows.documents import DocumentsWorkflow; print('documents workflow import ok')"
python -c "from workflows.documents.runtime import plan_task, run_task; print('documents runtime import ok')"
python -c "from workflows.documents.agents.indexer import IndexerAgent, IndexerOutput; from workflows.documents.agents.retriever import RetrieverAgent, RetrieverOutput; from workflows.documents.agents.answerer import AnswerAgent, AnswererOutput; print('documents agents import ok')"
python -c "from workflows.documents.reports.final_report import DocumentChatReport; from workflows.documents.reports.markdown import render_document_chat_report_markdown; print('documents reports import ok')"

# file_organization workflow smoke tests (root project)
python -c "import sys; sys.path.insert(0, '.'); import workflows.file_organization; print('file_organization workflow registered:', [e.id for e in __import__('core.capability_registry', fromlist=['list_workflows']).list_workflows()])"
python -c "from workflows.file_organization import FileOrganizationWorkflow; print('file_organization workflow import ok')"
python -c "from workflows.file_organization.runtime import plan_task, run_task; print('file_organization runtime import ok')"
python -c "from workflows.file_organization.agents.analyzer import AnalyzerAgent, AnalyzerResult; from workflows.file_organization.agents.proposer import ProposerAgent, ProposerResult; from workflows.file_organization.agents.applier import ApplierAgent, ApplierResult; print('file_organization agents import ok')"
python -c "from workflows.file_organization.reports.final_report import FileOrganizationReport; from workflows.file_organization.reports.markdown import render_file_organization_markdown; print('file_organization reports import ok')"

# presets smoke tests (root project)
python -c "from presets import PRESET_REGISTRY; print('presets registered:', [p.preset_id for p in PRESET_REGISTRY.list()])"
python -c "from presets.codebase_assistant import CodebaseAssistantPreset; print('codebase preset ok')"
python -c "from presets.local_document_chat import LocalDocumentChatPreset; print('documents preset ok')"
python -c "from presets.research_report import ResearchReportPreset; print('research preset ok')"
python -c "from presets.file_organizer import FileOrganizerPreset; print('file org preset ok')"
python -c "from presets.docs_maintainer import DocsMaintainerPreset; print('docs maintainer preset ok')"
python -c "from presets.github_maintainer import GitHubMaintainerPreset; print('github preset ok')"
python -c "from presets.command_assistant import CommandAssistantPreset; print('command preset ok')"
python -c "from interfaces.guided_tui.app import run_guided_tui; print('guided TUI import ok')"
python interfaces/cli/cli.py presets
python interfaces/cli/cli.py start codebase-assistant --help
python interfaces/cli/cli.py guided --help

# guided_tui smoke tests (root project)
python -c "from interfaces.guided_tui import run_guided_tui; print('guided_tui import ok')"
python -m py_compile interfaces/guided_tui/__init__.py interfaces/guided_tui/app.py interfaces/guided_tui/picker.py interfaces/guided_tui/questionnaire.py interfaces/guided_tui/render.py

# brain memory smoke tests (root project)
python -c "from pathlib import Path; from memory.brain import Brain; b = Brain(Path('.')); b.perceive('test','action','ok'); print('brain ok')"
python -c "from pathlib import Path; from memory.episodic import EpisodicMemory; e = EpisodicMemory(Path('.ai-team/memory/episodes')); e.record('ctx','act'); print('episodic ok')"
python -c "from pathlib import Path; from memory.semantic import SemanticMemory; s = SemanticMemory(Path('.ai-team/memory/semantic')); s.learn('x','X'); print('semantic ok')"
python -c "from memory.embeddings import get_engine; v = get_engine().encode('hello'); print('embedding dim:', len(v))"
python -c "from pathlib import Path; from memory.bus import MemoryBus; b = MemoryBus(Path('.')); b.write('jsonl','k',{'v':1}); print('bus ok')"

# memory tier smoke tests (root project)
python -c "from memory.tiers.working import WorkingMemory; wm = WorkingMemory(); wm.set('k','v'); print('working memory ok:', wm.get('k'))"
python -c "from memory.tiers.global_ import GlobalMemory; gm = GlobalMemory(base_path=Path('.ai-team/memory/global-test')); gm.set_preference('theme','dark'); print('global memory ok:', gm.get_preference('theme'))"
python -c "from memory import WorkingMemory, GlobalMemory; print('memory tier exports ok')"

# run full memory test suite (target: 100+ tests)
$env:PYTHONPATH="."; pytest tests\memory -v

# run core module unit tests
$env:PYTHONPATH="."; pytest tests\core -v

# run smoke tests (workflows, presets, CLI)
$env:PYTHONPATH="."; pytest tests\smoke -v

# run MCP tests
$env:PYTHONPATH="."; pytest tests\test_mcp.py -v

# run browser tool tests
$env:PYTHONPATH="."; pytest tests\test_browser_tool.py -v

# run local_db tool tests
$env:PYTHONPATH="."; pytest tests\test_local_db_tool.py -v

# run Web UI tests
$env:PYTHONPATH="."; pytest tests\test_web_ui.py -v

# run API server tests
$env:PYTHONPATH="."; pytest tests\test_api_server.py -v

# run distributed worker tests
$env:PYTHONPATH="."; pytest tests\test_distributed.py -v

# run marketplace tests
$env:PYTHONPATH="."; pytest tests\test_marketplace.py -v

# run monitoring tests
$env:PYTHONPATH="."; pytest tests\test_monitoring.py -v

# run self-improving tests
$env:PYTHONPATH="."; pytest tests\test_self_improving.py -v

# run multimodal tests
$env:PYTHONPATH="."; pytest tests\test_multimodal.py -v

# run federation tests
$env:PYTHONPATH="."; pytest tests\test_federation.py -v

# run desktop UI tests
$env:PYTHONPATH="."; pytest tests\test_desktop_ui.py -v

# run full root test suite
$env:PYTHONPATH="."; pytest tests\ -v
