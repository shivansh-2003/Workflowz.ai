"""AI workflow router — generate plan, clarification, approve, reject."""

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import bad_request, forbidden, not_found
from app.crud.ai_workflow import (
    create_workflow_state,
    get_workflow_state,
    persist_ai_plan,
    update_workflow_state,
)
from app.crud.project import get_project
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.tenancy import get_org_context
from app.schemas.ai_workflow import (
    AIGenerateRequest,
    AIGenerateResponse,
    AIApprovalRequest,
    AIApprovalResponse,
    AIClarificationResponse,
    AIPlanResponse,
    AIStatusResponse,
)

from app.agents.orchestrator import run_pipeline_background, run_pipeline_resume_background

router = APIRouter(prefix="/projects/{project_id}/ai", tags=["ai"])


def _require_head_or_superuser(current_user, org_context):
    """Raise 403 if user is not org head or superuser."""
    if not current_user.is_superuser and org_context.position != "head":
        raise forbidden("Organization head access required.")


@router.post("/generate", response_model=AIGenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_ai_pipeline(
    project_id: int,
    payload: AIGenerateRequest,
    organization_name: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """Start AI pipeline as background task."""
    if current_user.is_superuser:
        if not organization_name:
            raise bad_request("organization_name is required for superuser.")
        org_name = organization_name
    else:
        org_context = await get_org_context(db, current_user)
        _require_head_or_superuser(current_user, org_context)
        org_name = org_context.organization_name

    project = await get_project(db, org_name, project_id)
    if not project:
        raise not_found("Project not found.")

    # Merge project description if not provided
    text_desc = payload.text_description or (project.project_description or "")
    wf = await create_workflow_state(
        db,
        org_name,
        project_id,
        text_description=text_desc,
        markdown_content=payload.markdown_content,
    )
    background_tasks.add_task(
        run_pipeline_background,
        project_id=project_id,
        organization_name=org_name,
        workflow_id=wf.id,
    )
    return AIGenerateResponse(workflow_id=wf.id, status="started")


@router.get("/status", response_model=AIStatusResponse)
async def get_ai_status(
    project_id: int,
    organization_name: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Poll current AI workflow state."""
    if current_user.is_superuser:
        if not organization_name:
            raise bad_request("organization_name is required for superuser.")
        org_name = organization_name
    else:
        org_context = await get_org_context(db, current_user)
        org_name = org_context.organization_name

    wf = await get_workflow_state(db, org_name, project_id)
    if not wf:
        raise not_found("No AI workflow found for this project.")
    return AIStatusResponse(
        workflow_id=wf.id,
        current_state=wf.current_state,
        locked=wf.locked,
        error=wf.error,
        agent_outputs=wf.agent_outputs,
        updated_at=wf.updated_at,
    )


@router.get("/plan", response_model=AIPlanResponse)
async def get_ai_plan(
    project_id: int,
    organization_name: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get generated plan (available after HUMAN_APPROVAL state)."""
    if current_user.is_superuser:
        if not organization_name:
            raise bad_request("organization_name is required for superuser.")
        org_name = organization_name
    else:
        org_context = await get_org_context(db, current_user)
        org_name = org_context.organization_name

    wf = await get_workflow_state(db, org_name, project_id)
    if not wf:
        raise not_found("No AI workflow found for this project.")
    if wf.current_state != "HUMAN_APPROVAL":
        raise bad_request(
            f"Plan not ready. Current state: {wf.current_state}. "
            "Wait for pipeline to reach HUMAN_APPROVAL."
        )

    outputs = wf.agent_outputs or {}
    task_output = outputs.get("task_output") or {}
    matching_output = outputs.get("matching_output") or {}
    risk_output = outputs.get("risk_output") or {}

    return AIPlanResponse(
        task_groups=task_output.get("task_groups", []),
        assignments=matching_output.get("assignments", []),
        unassigned_tasks=matching_output.get("unassigned_tasks", []),
        risk_report=risk_output,
        team_capability_model=outputs.get("team_capability_model"),
        warnings=matching_output.get("warnings", []),
    )


@router.post("/clarification", status_code=status.HTTP_200_OK)
async def submit_clarification(
    project_id: int,
    payload: AIClarificationResponse,
    organization_name: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """Submit clarification answers and resume pipeline."""
    if current_user.is_superuser:
        if not organization_name:
            raise bad_request("organization_name is required for superuser.")
        org_name = organization_name
    else:
        org_context = await get_org_context(db, current_user)
        _require_head_or_superuser(current_user, org_context)
        org_name = org_context.organization_name

    wf = await get_workflow_state(db, org_name, project_id)
    if not wf:
        raise not_found("No AI workflow found for this project.")
    if wf.current_state != "WAIT_FOR_USER":
        raise bad_request(
            f"Workflow not waiting for clarification. Current state: {wf.current_state}."
        )
    if not wf.locked:
        raise bad_request("Workflow is not locked for clarification.")

    await update_workflow_state(
        db,
        wf,
        clarification_answers=payload.answers,
        locked=False,
    )
    background_tasks.add_task(run_pipeline_resume_background, workflow_id=wf.id)
    return {"status": "resumed"}


@router.post("/approve", response_model=AIApprovalResponse)
async def approve_plan(
    project_id: int,
    payload: AIApprovalRequest,
    organization_name: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve plan and persist tasks to DB."""
    if not payload.approved:
        raise bad_request("Use /reject to reject the plan.")

    if current_user.is_superuser:
        if not organization_name:
            raise bad_request("organization_name is required for superuser.")
        org_name = organization_name
    else:
        org_context = await get_org_context(db, current_user)
        _require_head_or_superuser(current_user, org_context)
        org_name = org_context.organization_name

    wf = await get_workflow_state(db, org_name, project_id)
    if not wf:
        raise not_found("No AI workflow found for this project.")
    if wf.current_state != "HUMAN_APPROVAL":
        raise bad_request(
            f"Plan not in HUMAN_APPROVAL state. Current state: {wf.current_state}."
        )

    tasks_created, tasks_skipped, progress = await persist_ai_plan(
        db, org_name, project_id, wf, edits=payload.edits
    )
    return AIApprovalResponse(
        tasks_created=tasks_created,
        tasks_skipped=tasks_skipped,
        project_progress=progress,
    )


@router.post("/reject", status_code=status.HTTP_200_OK)
async def reject_plan(
    project_id: int,
    organization_name: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reject the AI-generated plan."""
    if current_user.is_superuser:
        if not organization_name:
            raise bad_request("organization_name is required for superuser.")
        org_name = organization_name
    else:
        org_context = await get_org_context(db, current_user)
        _require_head_or_superuser(current_user, org_context)
        org_name = org_context.organization_name

    wf = await get_workflow_state(db, org_name, project_id)
    if not wf:
        raise not_found("No AI workflow found for this project.")
    if wf.current_state != "HUMAN_APPROVAL":
        raise bad_request(
            f"Plan not in HUMAN_APPROVAL state. Current state: {wf.current_state}."
        )

    await update_workflow_state(db, wf, current_state="TERMINATED")
    return {"status": "rejected"}
