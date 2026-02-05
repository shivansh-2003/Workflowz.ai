from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    project_name: str
    project_description: str | None = None


class ProjectUpdate(BaseModel):
    project_name: str | None = None
    project_description: str | None = None
    project_progress: int | None = Field(default=None, ge=0, le=100)


class ProjectOut(BaseModel):
    organization_name: str
    project_id: int
    project_name: str
    project_description: str | None
    project_progress: int
    created_by: str

    model_config = {"from_attributes": True}
