from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import TeamMember, User


@dataclass(frozen=True)
class OrgContext:
    organization_name: str
    member_id: int
    position: str


async def get_org_context(db: AsyncSession, current_user: User) -> OrgContext:
    result = await db.execute(
        select(TeamMember).where(TeamMember.user_id == current_user.id)
    )
    team_member = result.scalar_one_or_none()
    if team_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not assigned to any organization.",
        )
    return OrgContext(
        organization_name=team_member.organization_name,
        member_id=team_member.member_id,
        position=team_member.position,
    )
