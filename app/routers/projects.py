from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import bad_request, forbidden, not_found
from app.crud.project import create_project, delete_project, get_project, get_projects, update_project
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.tenancy import get_org_context
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=list[ProjectOut])
async def list_projects(
    organization_name: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ProjectOut]:
    if current_user.is_superuser:
        if not organization_name:
            raise bad_request("organization_name is required for superuser.")
        org_name = organization_name
    else:
        org_context = await get_org_context(db, current_user)
        org_name = org_context.organization_name

    projects = await get_projects(db, org_name)
    return [ProjectOut.model_validate(project) for project in projects]


@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_new_project(
    payload: ProjectCreate,
    organization_name: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectOut:
    if current_user.is_superuser:
        if not organization_name:
            raise bad_request("organization_name is required for superuser.")
        org_name = organization_name
        created_by = current_user.email
    else:
        org_context = await get_org_context(db, current_user)
        if org_context.position != "head":
            raise forbidden("Organization head access required.")
        org_name = org_context.organization_name
        created_by = current_user.email

    project = await create_project(
        db, org_name, payload.project_name, payload.project_description, created_by
    )
    return ProjectOut.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectOut)
async def update_project_by_id(
    project_id: int,
    payload: ProjectUpdate,
    organization_name: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectOut:
    if current_user.is_superuser:
        if not organization_name:
            raise bad_request("organization_name is required for superuser.")
        org_name = organization_name
    else:
        org_context = await get_org_context(db, current_user)
        if org_context.position != "head":
            raise forbidden("Organization head access required.")
        org_name = org_context.organization_name

    project = await get_project(db, org_name, project_id)
    if project is None:
        raise not_found("Project not found.")
    updated = await update_project(db, project, payload.model_dump(exclude_unset=True))
    return ProjectOut.model_validate(updated)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_by_id(
    project_id: int,
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

    project = await get_project(db, org_name, project_id)
    if project is None:
        raise not_found("Project not found.")
    await delete_project(db, project)
