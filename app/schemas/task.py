from datetime import date

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    task_description: str
    task_deadline: date | None = None
    task_assigned_to: int
    task_importance: str | None = Field(
        default=None, pattern="^(high|medium|low)$"
    )


class TaskUpdate(BaseModel):
    task_description: str | None = None
    task_deadline: date | None = None
    task_assigned_to: int | None = None
    task_importance: str | None = Field(
        default=None, pattern="^(high|medium|low)$"
    )


class TaskCompleteUpdate(BaseModel):
    task_completed: bool


class TaskOut(BaseModel):
    organization_name: str
    project_id: int
    task_id: int
    task_description: str
    task_deadline: date | None
    task_assigned_to: int
    task_importance: str | None
    task_completed: bool

    model_config = {"from_attributes": True}
