from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Task


async def get_tasks(
    db: AsyncSession, organization_name: str, project_id: int
) -> list[Task]:
    result = await db.execute(
        select(Task).where(
            Task.organization_name == organization_name,
            Task.project_id == project_id,
        )
    )
    return list(result.scalars().all())


async def get_task(
    db: AsyncSession, organization_name: str, project_id: int, task_id: int
) -> Task | None:
    result = await db.execute(
        select(Task).where(
            Task.organization_name == organization_name,
            Task.project_id == project_id,
            Task.task_id == task_id,
        )
    )
    return result.scalar_one_or_none()


async def create_task(
    db: AsyncSession,
    organization_name: str,
    project_id: int,
    task_description: str,
    task_deadline,
    task_assigned_to: int,
    task_importance: str | None,
) -> Task:
    task = Task(
        organization_name=organization_name,
        project_id=project_id,
        task_description=task_description,
        task_deadline=task_deadline,
        task_assigned_to=task_assigned_to,
        task_importance=task_importance,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def update_task(db: AsyncSession, task: Task, data: dict) -> Task:
    for key, value in data.items():
        setattr(task, key, value)
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task: Task) -> None:
    await db.delete(task)
    await db.commit()
