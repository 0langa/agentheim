from __future__ import annotations

from core.public_api import register_workflow

from workflows.command_assistant.workflows.command_assistant import CommandAssistantWorkflow
from workflows.coding.workflows.coding import CodingWorkflow
from workflows.context_maintainer.workflow import ContextMaintainerWorkflow
from workflows.docs_maintenance.workflows.docs_maintenance import DocsMaintenanceWorkflow
from workflows.documents.workflows.documents import DocumentsWorkflow
from workflows.file_organization.workflows.file_organization import FileOrganizationWorkflow
from workflows.github_maintenance.workflows.github_maintenance import GitHubMaintenanceWorkflow
from workflows.research.workflows.research import ResearchWorkflow


BUILTIN_WORKFLOWS = (
    CommandAssistantWorkflow,
    CodingWorkflow,
    ContextMaintainerWorkflow,
    DocsMaintenanceWorkflow,
    DocumentsWorkflow,
    FileOrganizationWorkflow,
    GitHubMaintenanceWorkflow,
    ResearchWorkflow,
)


def register_builtin_workflows() -> None:
    for workflow_cls in BUILTIN_WORKFLOWS:
        try:
            register_workflow(
                workflow_cls,
                metadata={
                    "workflow_id": workflow_cls.workflow_id,
                    "support_state": workflow_cls.support_state,
                },
            )
        except ValueError:
            continue
