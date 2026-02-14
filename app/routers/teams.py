from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import bad_request, forbidden, not_found
from app.crud.team import create_team_member, get_team_members
from app.crud.user import get_user_by_email
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.tenancy import get_org_context
from app.schemas.team import TeamMemberCreate, TeamMemberOut

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("/internal/capability-model", response_model=list[TeamMemberOut])
async def get_team_for_agents(
    organization_name: str = Query(..., description="Organization name"),
    db: AsyncSession = Depends(get_db),
) -> list[TeamMemberOut]:
    """Internal endpoint for AI agents (e.g. Streamlit) to fetch team capability model. No auth required."""
    if not organization_name:
        raise bad_request("organization_name is required.")
    members = await get_team_members(db, organization_name)
    return [TeamMemberOut.model_validate(member) for member in members]


@router.get("/", response_model=list[TeamMemberOut])
async def list_team_members(
    organization_name: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TeamMemberOut]:
    if current_user.is_superuser:
        if not organization_name:
            raise bad_request("organization_name is required for superuser.")
        org_name = organization_name
    else:
        org_context = await get_org_context(db, current_user)
        if org_context.position != "head":
            raise forbidden("Organization head access required.")
        org_name = org_context.organization_name

    members = await get_team_members(db, org_name)
    return [TeamMemberOut.model_validate(member) for member in members]


@router.post("/", response_model=TeamMemberOut, status_code=status.HTTP_201_CREATED)
async def add_team_member(
    payload: TeamMemberCreate,
    organization_name: str | None = Query(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TeamMemberOut:
    if payload.position not in {"head", "member"}:
        raise bad_request("position must be 'head' or 'member'.")

    if current_user.is_superuser:
        if not organization_name:
            raise bad_request("organization_name is required for superuser.")
        org_name = organization_name
    else:
        org_context = await get_org_context(db, current_user)
        if org_context.position != "head":
            raise forbidden("Organization head access required.")
        org_name = org_context.organization_name

    user = await get_user_by_email(db, payload.email)
    if user is None:
        raise not_found("User does not exist.")

    member = await create_team_member(
        db=db,
        organization_name=org_name,
        name=payload.name,
        email=payload.email,
        designation=payload.designation,
        position=payload.position,
        user_id=user.id,
    )
    return TeamMemberOut.model_validate(member)
