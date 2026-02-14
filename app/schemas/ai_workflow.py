"""Schemas for AI workflow API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AIGenerateRequest(BaseModel):
    """Request to start AI pipeline for a project."""

    text_description: str | None = None
    markdown_content: str | None = None


class AIGenerateResponse(BaseModel):
    """Response when AI pipeline is started."""

    workflow_id: int
    status: str = "started"


class AIStatusResponse(BaseModel):
    """Current AI workflow state for polling."""

    workflow_id: int
    current_state: str
    locked: bool
    error: str | None = None
    agent_outputs: dict[str, Any] | None = None
    updated_at: datetime | None = None


class AIPlanResponse(BaseModel):
    """Generated plan (tasks, assignments, risk report) for human approval."""

    task_groups: list[dict[str, Any]] = Field(default_factory=list)
    assignments: list[dict[str, Any]] = Field(default_factory=list)
    unassigned_tasks: list[dict[str, Any]] = Field(default_factory=list)
    risk_report: dict[str, Any] | None = None
    team_capability_model: dict[str, Any] | None = None
    warnings: list[str] = Field(default_factory=list)


class AIClarificationResponse(BaseModel):
    """User answers to clarification questions."""

    answers: dict[str, Any] = Field(default_factory=dict)


class AIApprovalRequest(BaseModel):
    """Request to approve or reject the AI-generated plan."""

    approved: bool
    edits: list[dict[str, Any]] | None = Field(
        default=None, description="Optional task edits before persist"
    )


class AIApprovalResponse(BaseModel):
    """Response after approving and persisting the plan."""

    tasks_created: int = 0
    tasks_skipped: int = 0
    project_progress: int = 0
