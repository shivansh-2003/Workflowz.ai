from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import TeamMember


async def get_team_members(db: AsyncSession, organization_name: str) -> list[TeamMember]:
    result = await db.execute(
        select(TeamMember).where(TeamMember.organization_name == organization_name)
    )
    return list(result.scalars().all())


async def get_team_member_by_id(
    db: AsyncSession, organization_name: str, member_id: int
) -> TeamMember | None:
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.organization_name == organization_name,
            TeamMember.member_id == member_id,
        )
    )
    return result.scalar_one_or_none()


async def get_team_member_by_user_id(
    db: AsyncSession, user_id: int
) -> TeamMember | None:
    result = await db.execute(select(TeamMember).where(TeamMember.user_id == user_id))
    return result.scalar_one_or_none()


async def get_team_member_by_email(
    db: AsyncSession, organization_name: str, email: str
) -> TeamMember | None:
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.organization_name == organization_name,
            TeamMember.email == email,
        )
    )
    return result.scalar_one_or_none()


async def create_team_member(
    db: AsyncSession,
    organization_name: str,
    name: str,
    email: str,
    designation: str | None,
    position: str,
    user_id: int,
) -> TeamMember:
    member = TeamMember(
        organization_name=organization_name,
        name=name,
        email=email,
        designation=designation,
        position=position,
        user_id=user_id,
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member
