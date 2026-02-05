from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Project, Task


async def get_projects(db: AsyncSession, organization_name: str) -> list[Project]:
    result = await db.execute(
        select(Project).where(Project.organization_name == organization_name)
    )
    return list(result.scalars().all())


async def get_project(
    db: AsyncSession, organization_name: str, project_id: int
) -> Project | None:
    result = await db.execute(
        select(Project).where(
            Project.organization_name == organization_name,
            Project.project_id == project_id,
        )
    )
    return result.scalar_one_or_none()


async def create_project(
    db: AsyncSession,
    organization_name: str,
    project_name: str,
    project_description: str | None,
    created_by: str,
) -> Project:
    project = Project(
        organization_name=organization_name,
        project_name=project_name,
        project_description=project_description,
        created_by=created_by,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def update_project(
    db: AsyncSession, project: Project, data: dict
) -> Project:
    for key, value in data.items():
        setattr(project, key, value)
    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project: Project) -> None:
    await db.delete(project)
    await db.commit()


async def recalculate_project_progress(
    db: AsyncSession, organization_name: str, project_id: int
) -> int:
    result = await db.execute(
        select(Task).where(
            Task.organization_name == organization_name,
            Task.project_id == project_id,
        )
    )
    tasks = list(result.scalars().all())
    if not tasks:
        progress = 0
    else:
        weight_map = {"high": 3, "medium": 2, "low": 1, None: 1}
        total_weight = 0
        completed_weight = 0
        for task in tasks:
            weight = weight_map.get(task.task_importance, 1)
            total_weight += weight
            if task.task_completed:
                completed_weight += weight
        progress = int((completed_weight / total_weight) * 100) if total_weight else 0

    project = await get_project(db, organization_name, project_id)
    if project is not None:
        project.project_progress = progress
        await db.commit()
        await db.refresh(project)
    return progress
