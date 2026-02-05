# Schemas

Pydantic models for request/response validation and serialization.

## Overview

This directory contains Pydantic schema models that define the structure of API requests and responses. These schemas provide automatic validation, serialization, and API documentation.

## Files

### `auth.py`
Authentication-related schemas.

**Schemas:**
- `UserCreate` - User registration request
- `UserOut` - User response model
- `Token` - JWT token response

**Usage:**
```python
from app.schemas.auth import UserCreate, UserOut

@router.post("/signup", response_model=UserOut)
async def signup(payload: UserCreate):
    # payload.email and payload.password are validated
    user = await create_user(db, payload.email, payload.password)
    return UserOut.model_validate(user)
```

**Fields:**
- `UserCreate`: `email` (EmailStr), `password` (8-72 chars), `is_superuser` (bool)
- `UserOut`: `id`, `email`, `is_superuser`, `created_at`
- `Token`: `access_token`, `token_type`

### `organization.py`
Organization-related schemas.

**Schemas:**
- `OrganizationCreate` - Organization creation request
- `OrganizationRename` - Organization rename request
- `OrganizationOut` - Organization response with details

**Usage:**
```python
from app.schemas.organization import OrganizationCreate

@router.post("/organizations/")
async def create_org(payload: OrganizationCreate):
    # payload.organization_name, payload.head_email validated
    pass
```

**Fields:**
- `OrganizationCreate`: `organization_name`, `head_email`, `head_name`, `head_designation`
- `OrganizationOut`: `organization_name`, `head_name`, `head_email`, `member_count`

### `team.py`
Team member-related schemas.

**Schemas:**
- `TeamMemberCreate` - Team member creation request
- `TeamMemberOut` - Team member response

**Usage:**
```python
from app.schemas.team import TeamMemberCreate, TeamMemberOut

@router.post("/teams", response_model=TeamMemberOut)
async def add_member(payload: TeamMemberCreate):
    member = await create_team_member(db, ...)
    return TeamMemberOut.model_validate(member)
```

**Fields:**
- `TeamMemberCreate`: `name`, `email`, `designation`, `position`
- `TeamMemberOut`: All team member fields including IDs

### `project.py`
Project-related schemas.

**Schemas:**
- `ProjectCreate` - Project creation request
- `ProjectUpdate` - Project update request
- `ProjectOut` - Project response

**Usage:**
```python
from app.schemas.project import ProjectCreate, ProjectOut

@router.post("/projects", response_model=ProjectOut)
async def create_project(payload: ProjectCreate):
    project = await create_project(db, ...)
    return ProjectOut.model_validate(project)
```

**Fields:**
- `ProjectCreate`: `project_name`, `project_description`
- `ProjectUpdate`: Optional fields for updates
- `ProjectOut`: All project fields including progress

### `task.py`
Task-related schemas.

**Schemas:**
- `TaskCreate` - Task creation request
- `TaskUpdate` - Task update request
- `TaskOut` - Task response

**Usage:**
```python
from app.schemas.task import TaskCreate, TaskOut

@router.post("/tasks", response_model=TaskOut)
async def create_task(payload: TaskCreate):
    task = await create_task(db, ...)
    return TaskOut.model_validate(task)
```

**Fields:**
- `TaskCreate`: `task_description`, `task_deadline`, `task_assigned_to`, `task_importance`
- `TaskUpdate`: Optional fields for updates
- `TaskOut`: All task fields including completion status

## Schema Design Patterns

### Base Models
Use Pydantic `BaseModel` for all schemas:
```python
from pydantic import BaseModel

class MySchema(BaseModel):
    field: str
```

### Field Validation
Use Pydantic validators for custom validation:
```python
from pydantic import Field, EmailStr

class UserCreate(BaseModel):
    email: EmailStr  # Automatic email validation
    password: str = Field(min_length=8, max_length=72)
```

### Optional Fields
Use `Optional` or default values:
```python
from typing import Optional

class TaskCreate(BaseModel):
    description: str
    deadline: Optional[date] = None
```

### Response Models
Use `model_validate()` to convert ORM models:
```python
from app.database.models import Project

project = await get_project(db, ...)
return ProjectOut.model_validate(project)
```

## Validation Features

### Automatic Validation
Pydantic automatically validates:
- Type checking (str, int, bool, etc.)
- Required fields
- Field constraints (min_length, max_length, etc.)
- Email format (EmailStr)
- Date format (date, datetime)

### Custom Validation
Add validators for complex rules:
```python
from pydantic import field_validator

class MySchema(BaseModel):
    value: str
    
    @field_validator('value')
    @classmethod
    def validate_value(cls, v):
        if not v.startswith('prefix'):
            raise ValueError('Must start with prefix')
        return v
```

### Error Messages
Validation errors are automatically formatted:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

## Usage in Routers

### Request Validation
```python
@router.post("/endpoint")
async def my_endpoint(payload: MySchema):
    # payload is automatically validated
    # Invalid requests return 422 Unprocessable Entity
    pass
```

### Response Serialization
```python
@router.get("/endpoint", response_model=MySchemaOut)
async def my_endpoint():
    data = get_data()
    return MySchemaOut.model_validate(data)
```

### Partial Updates
```python
@router.patch("/endpoint")
async def update_endpoint(
    payload: MySchemaUpdate,  # All fields optional
    id: int
):
    # Only provided fields are updated
    pass
```

## Best Practices

1. **Separate create/update schemas**: Different schemas for creation vs updates
2. **Use response models**: Always define response schemas for type safety
3. **Validate early**: Let Pydantic handle validation before business logic
4. **Document fields**: Add Field descriptions for API docs
5. **Use appropriate types**: EmailStr, date, datetime for proper validation
6. **Handle None**: Use Optional for nullable fields
7. **Reuse schemas**: Create base schemas and extend them

## Adding New Schemas

When adding a new schema:

1. Create schema class inheriting from `BaseModel`
2. Define fields with appropriate types
3. Add Field constraints (min_length, max_length, etc.)
4. Use EmailStr for emails, date/datetime for dates
5. Create separate schemas for create/update/response
6. Document fields with Field descriptions

**Example:**
```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date

class MyModelCreate(BaseModel):
    """Schema for creating MyModel."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    value: Optional[int] = Field(None, ge=0)

class MyModelOut(BaseModel):
    """Schema for MyModel response."""
    id: int
    name: str
    email: str
    value: Optional[int]
    created_at: datetime
```

## Schema Relationships

Schemas can reference other schemas:
```python
class ProjectOut(BaseModel):
    project_id: int
    project_name: str
    tasks: list[TaskOut]  # Reference to TaskOut schema
```

This enables nested response structures for related data.
