from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import bad_request, not_found
from app.crud.team import create_team_member, get_team_member_by_email, get_team_members
from app.crud.user import get_user_by_email
from app.database.models import Project, Task, TeamMember, User
from app.database.session import get_db
from app.dependencies.auth import get_current_superuser
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationHeadUpdate,
    OrganizationRename,
)
from app.schemas.team import TeamMemberOut

router = APIRouter(prefix="/superuser/organizations", tags=["superuser"])


@router.post("/", response_model=TeamMemberOut)
async def create_organization(
    payload: OrganizationCreate,
    _: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
) -> TeamMemberOut:
    if payload.organization_name.strip() == "":
        raise bad_request("Organization name cannot be empty.")

    existing_org = await get_team_members(db, payload.organization_name)
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization already exists.",
        )

    head_user = await get_user_by_email(db, payload.head_email)
    if head_user is None:
        raise not_found("Head user does not exist.")

    member = await create_team_member(
        db=db,
        organization_name=payload.organization_name,
        name=payload.head_name,
        email=payload.head_email,
        designation=payload.head_designation,
        position="head",
        user_id=head_user.id,
    )
    return TeamMemberOut.model_validate(member)


@router.patch("/{organization_name}")
async def update_organization_name(
    organization_name: str,
    payload: OrganizationRename,
    _: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if payload.new_name.strip() == "":
        raise bad_request("New organization name cannot be empty.")

    existing_org = await get_team_members(db, organization_name)
    if not existing_org:
        raise not_found("Organization not found.")

    existing_new = await get_team_members(db, payload.new_name)
    if existing_new:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="New organization name already exists.",
        )

    await db.execute(
        update(TeamMember)
        .where(TeamMember.organization_name == organization_name)
        .values(organization_name=payload.new_name)
    )
    await db.execute(
        update(Project)
        .where(Project.organization_name == organization_name)
        .values(organization_name=payload.new_name)
    )
    await db.execute(
        update(Task)
        .where(Task.organization_name == organization_name)
        .values(organization_name=payload.new_name)
    )
    await db.commit()
    return {"status": "updated", "organization_name": payload.new_name}


@router.patch("/{organization_name}/head", response_model=TeamMemberOut)
async def change_organization_head(
    organization_name: str,
    payload: OrganizationHeadUpdate,
    _: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
) -> TeamMemberOut:
    existing_org = await get_team_members(db, organization_name)
    if not existing_org:
        raise not_found("Organization not found.")

    new_head_user = await get_user_by_email(db, payload.new_head_email)
    if new_head_user is None:
        raise not_found("User for new head does not exist.")

    new_head_member = await get_team_member_by_email(
        db, organization_name, payload.new_head_email
    )
    if new_head_member is None:
        raise not_found("New head must be an existing team member.")

    result = await db.execute(
        select(TeamMember).where(
            TeamMember.organization_name == organization_name,
            TeamMember.position == "head",
        )
    )
    current_head = result.scalar_one_or_none()
    if current_head is None:
        raise not_found("Current organization head not found.")

    current_head.position = "member"
    new_head_member.position = "head"
    await db.commit()
    await db.refresh(new_head_member)
    return TeamMemberOut.model_validate(new_head_member)
