from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import bad_request, forbidden, not_found
from app.crud.project import recalculate_project_progress
from app.crud.task import create_task, delete_task, get_task, get_tasks, update_task
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.tenancy import get_org_context
from app.schemas.task import TaskCompleteUpdate, TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])


@router.get("/", response_model=list[TaskOut])
async def list_tasks(
    project_id: int,
    organization_name: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TaskOut]:
    if current_user.is_superuser:
        if not organization_name:
            raise bad_request("organization_name is required for superuser.")
        org_name = organization_name
        tasks = await get_tasks(db, org_name, project_id)
    else:
        org_context = await get_org_context(db, current_user)
        org_name = org_context.organization_name
        tasks = await get_tasks(db, org_name, project_id)
        if org_context.position == "member":
            tasks = [task for task in tasks if task.task_assigned_to == org_context.member_id]

    return [TaskOut.model_validate(task) for task in tasks]


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    project_id: int,
    payload: TaskCreate,
    organization_name: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskOut:
    if current_user.is_superuser:
        if not organization_name:
            raise bad_request("organization_name is required for superuser.")
        org_name = organization_name
    else:
        org_context = await get_org_context(db, current_user)
        if org_context.position != "head":
            raise forbidden("Organization head access required.")
        org_name = org_context.organization_name

    task = await create_task(
        db=db,
        organization_name=org_name,
        project_id=project_id,
        task_description=payload.task_description,
        task_deadline=payload.task_deadline,
        task_assigned_to=payload.task_assigned_to,
        task_importance=payload.task_importance,
    )
    await recalculate_project_progress(db, org_name, project_id)
    return TaskOut.model_validate(task)


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task_by_id(
    project_id: int,
    task_id: int,
    payload: TaskUpdate,
    organization_name: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskOut:
    if current_user.is_superuser:
        if not organization_name:
            raise bad_request("organization_name is required for superuser.")
        org_name = organization_name
    else:
        org_context = await get_org_context(db, current_user)
        if org_context.position != "head":
            raise forbidden("Organization head access required.")
        org_name = org_context.organization_name

    task = await get_task(db, org_name, project_id, task_id)
    if task is None:
        raise not_found("Task not found.")
    updated = await update_task(db, task, payload.model_dump(exclude_unset=True))
    await recalculate_project_progress(db, org_name, project_id)
    return TaskOut.model_validate(updated)


@router.patch("/{task_id}/complete", response_model=TaskOut)
async def mark_task_complete(
    project_id: int,
    task_id: int,
    payload: TaskCompleteUpdate,
    organization_name: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskOut:
    if current_user.is_superuser:
        if not organization_name:
            raise bad_request("organization_name is required for superuser.")
        org_name = organization_name
        org_context = None
    else:
        org_context = await get_org_context(db, current_user)
        org_name = org_context.organization_name

    task = await get_task(db, org_name, project_id, task_id)
    if task is None:
        raise not_found("Task not found.")

    if not current_user.is_superuser:
        if org_context.position == "member" and task.task_assigned_to != org_context.member_id:
            raise forbidden("You can only update your assigned tasks.")

    updated = await update_task(db, task, {"task_completed": payload.task_completed})
    await recalculate_project_progress(db, org_name, project_id)
    return TaskOut.model_validate(updated)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_by_id(
    project_id: int,
    task_id: int,
    organization_name: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    if current_user.is_superuser:
        if not organization_name:
            raise bad_request("organization_name is required for superuser.")
        org_name = organization_name
    else:
        org_context = await get_org_context(db, current_user)
        if org_context.position != "head":
            raise forbidden("Organization head access required.")
        org_name = org_context.organization_name

    task = await get_task(db, org_name, project_id, task_id)
    if task is None:
        raise not_found("Task not found.")
    await delete_task(db, task)
    await recalculate_project_progress(db, org_name, project_id)
