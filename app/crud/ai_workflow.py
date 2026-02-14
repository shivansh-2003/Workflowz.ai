"""CRUD for AI workflow state."""

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.task import create_task
from app.crud.project import get_project, recalculate_project_progress
from app.crud.team import get_team_members
from app.database.models import AIWorkflowState, Project

logger = logging.getLogger(__name__)


async def create_workflow_state(
    db: AsyncSession,
    organization_name: str,
    project_id: int,
    text_description: str | None = None,
    markdown_content: str | None = None,
) -> AIWorkflowState:
    """Create initial workflow state."""
    thread_id = str(uuid.uuid4())
    wf = AIWorkflowState(
        organization_name=organization_name,
        project_id=project_id,
        current_state="INPUT_INGESTION",
        thread_id=thread_id,
        agent_outputs={
            "text_description": text_description,
            "markdown_content": markdown_content,
        },
    )
    db.add(wf)
    await db.commit()
    await db.refresh(wf)
    return wf


async def get_workflow_state(
    db: AsyncSession, organization_name: str, project_id: int
) -> AIWorkflowState | None:
    """Get current workflow state for project."""
    result = await db.execute(
        select(AIWorkflowState).where(
            AIWorkflowState.organization_name == organization_name,
            AIWorkflowState.project_id == project_id,
        ).order_by(AIWorkflowState.id.desc())
    )
    return result.scalars().first()


async def get_workflow_state_by_id(
    db: AsyncSession, workflow_id: int
) -> AIWorkflowState | None:
    """Get workflow state by ID."""
    result = await db.execute(
        select(AIWorkflowState).where(AIWorkflowState.id == workflow_id)
    )
    return result.scalar_one_or_none()


async def update_workflow_state(
    db: AsyncSession,
    workflow: AIWorkflowState,
    *,
    current_state: str | None = None,
    last_successful_state: str | None = None,
    locked: bool | None = None,
    error: str | None = None,
    agent_outputs: dict[str, Any] | None = None,
    clarification_answers: dict[str, Any] | None = None,
    thread_id: str | None = None,
) -> AIWorkflowState:
    """Update workflow state fields."""
    if current_state is not None:
        workflow.current_state = current_state
    if last_successful_state is not None:
        workflow.last_successful_state = last_successful_state
    if locked is not None:
        workflow.locked = locked
    if error is not None:
        workflow.error = error
    if agent_outputs is not None:
        workflow.agent_outputs = agent_outputs
    if clarification_answers is not None:
        workflow.clarification_answers = clarification_answers
    if thread_id is not None:
        workflow.thread_id = thread_id

    workflow.state_version += 1
    await db.commit()
    await db.refresh(workflow)
    return workflow


async def set_workflow_error(
    db: AsyncSession, workflow: AIWorkflowState, error_msg: str
) -> AIWorkflowState:
    """Move workflow to ERROR_STATE."""
    return await update_workflow_state(
        db,
        workflow,
        current_state="ERROR_STATE",
        locked=False,
        error=error_msg,
    )


def _build_capability_to_members(team_members: list) -> dict[str, list[int]]:
    """Build capability -> member_ids mapping."""
    cap_map: dict[str, list[int]] = {}
    for m in team_members:
        des = (getattr(m, "designation", None) or "backend").lower()
        mid = getattr(m, "member_id", None)
        if mid is not None:
            if des not in cap_map:
                cap_map[des] = []
            cap_map[des].append(mid)
        if getattr(m, "position", None) == "head":
            if "head" not in cap_map:
                cap_map["head"] = []
            cap_map["head"].append(mid)
    return cap_map


def _pick_member_round_robin(
    cap_map: dict[str, list[int]], counter: dict[str, int], capability: str
) -> int | None:
    """Pick next member_id for capability using round-robin."""
    cap_lower = (capability or "backend").lower()
    ids = cap_map.get(cap_lower) or cap_map.get("backend") or cap_map.get("head")
    if not ids:
        return None
    idx = counter.get(cap_lower, 0) % len(ids)
    counter[cap_lower] = counter.get(cap_lower, 0) + 1
    return ids[idx]


async def persist_ai_plan(
    db: AsyncSession,
    organization_name: str,
    project_id: int,
    workflow: AIWorkflowState,
    edits: list[dict[str, Any]] | None = None,
) -> tuple[int, int, int]:
    """
    Persist approved AI plan to tasks table.
    Returns (tasks_created, tasks_skipped, project_progress).
    """
    outputs = workflow.agent_outputs or {}
    task_output = outputs.get("task_output") or {}
    matching_output = outputs.get("matching_output") or {}
    team_capability_model = outputs.get("team_capability_model") or {}

    task_groups = task_output.get("task_groups", [])
    assignments = {a["task_id"]: a for a in matching_output.get("assignments", [])}
    edits_by_task_id = {e["task_id"]: e for e in (edits or [])} if edits else {}

    team_members = await get_team_members(db, organization_name)
    cap_map = _build_capability_to_members(team_members)
    counter: dict[str, int] = {}

    tasks_created = 0
    tasks_skipped = 0

    for grp in task_groups:
        for t in grp.get("tasks", []):
            task_id = t.get("task_id")
            status = t.get("status", "ready")
            if status == "blocked":
                tasks_skipped += 1
                continue

            desc = t.get("description", "")
            required_cap = t.get("required_capability", "backend")
            importance = "high" if status == "ready" else "medium"

            if edits_by_task_id and task_id in edits_by_task_id:
                ed = edits_by_task_id[task_id]
                if ed.get("skip"):
                    tasks_skipped += 1
                    continue
                desc = ed.get("description", desc)
                required_cap = ed.get("required_capability", required_cap)
                importance = ed.get("task_importance", importance)

            assign = assignments.get(task_id, {})
            assigned_to_cap = assign.get("assigned_to", required_cap)
            member_id = _pick_member_round_robin(cap_map, counter, assigned_to_cap)
            if member_id is None:
                member_id = _pick_member_round_robin(cap_map, counter, "head")
            if member_id is None and team_members:
                member_id = team_members[0].member_id

            if member_id is None:
                tasks_skipped += 1
                continue

            try:
                await create_task(
                    db=db,
                    organization_name=organization_name,
                    project_id=project_id,
                    task_description=desc,
                    task_deadline=None,
                    task_assigned_to=member_id,
                    task_importance=importance,
                )
                tasks_created += 1
            except Exception as e:
                logger.warning("persist_ai_plan: skip task %s: %s", task_id, e)
                tasks_skipped += 1

    progress = await recalculate_project_progress(db, organization_name, project_id)

    await update_workflow_state(
        db, workflow, current_state="COMPLETED", agent_outputs=outputs
    )

    return tasks_created, tasks_skipped, progress
