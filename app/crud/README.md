# CRUD

Database operations (Create, Read, Update, Delete) for all models.

## Overview

This directory contains CRUD (Create, Read, Update, Delete) operation modules that interact with the database using SQLAlchemy async ORM. Each module corresponds to a database model and provides functions for database operations.

## Files

### `user.py`
User-related database operations.

**Functions:**
- `get_user_by_email(db, email)` - Get user by email address
- `create_user(db, email, password, is_superuser)` - Create new user
- `get_user_by_id(db, user_id)` - Get user by ID

**Usage:**
```python
from app.crud.user import get_user_by_email, create_user

user = await get_user_by_email(db, "user@example.com")
new_user = await create_user(db, "new@example.com", "password", False)
```

### `team.py`
Team member-related database operations.

**Functions:**
- `get_team_members(db, organization_name)` - Get all members in organization
- `get_team_member(db, organization_name, member_id)` - Get specific member
- `create_team_member(db, ...)` - Add new team member
- `delete_team_member(db, organization_name, member_id)` - Remove member
- `get_all_organizations(db)` - Get all distinct organization names
- `get_organization_head(db, organization_name)` - Get organization head

**Usage:**
```python
from app.crud.team import get_team_members, create_team_member

members = await get_team_members(db, "my-org")
new_member = await create_team_member(
    db, "my-org", "John Doe", "john@example.com", "Developer", "member", user_id
)
```

### `project.py`
Project-related database operations.

**Functions:**
- `get_projects(db, organization_name)` - Get all projects in organization
- `get_project(db, organization_name, project_id)` - Get specific project
- `create_project(db, ...)` - Create new project
- `update_project(db, organization_name, project_id, ...)` - Update project
- `delete_project(db, organization_name, project_id)` - Delete project
- `calculate_project_progress(db, organization_name, project_id)` - Calculate progress percentage

**Usage:**
```python
from app.crud.project import get_projects, create_project

projects = await get_projects(db, "my-org")
new_project = await create_project(
    db, "my-org", "Project Name", "Description", "creator@example.com"
)
```

### `task.py`
Task-related database operations.

**Functions:**
- `get_tasks(db, organization_name, project_id)` - Get all tasks in project
- `get_task(db, organization_name, project_id, task_id)` - Get specific task
- `create_task(db, ...)` - Create new task
- `update_task(db, organization_name, project_id, task_id, ...)` - Update task
- `delete_task(db, organization_name, project_id, task_id)` - Delete task
- `toggle_task_completion(db, organization_name, project_id, task_id, completed)` - Toggle completion status

**Usage:**
```python
from app.crud.task import get_tasks, create_task

tasks = await get_tasks(db, "my-org", project_id=1)
new_task = await create_task(
    db, "my-org", 1, "Task description", deadline, member_id, "high"
)
```

## Design Patterns

### Async Operations
All CRUD functions are async and use SQLAlchemy's async session:
```python
async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
```

### Organization Scoping
Most operations are scoped by `organization_name` for multi-tenancy:
```python
async def get_projects(db: AsyncSession, organization_name: str) -> list[Project]:
    result = await db.execute(
        select(Project).where(Project.organization_name == organization_name)
    )
    return list(result.scalars().all())
```

### Error Handling
Functions return `None` for not found cases:
```python
user = await get_user_by_email(db, email)
if user is None:
    raise HTTPException(status_code=404, detail="User not found")
```

### Transaction Management
Database commits are handled in routers, not in CRUD functions:
```python
# In router
new_user = await create_user(db, email, password, False)
await db.commit()
await db.refresh(new_user)
```

## Common Operations

### Create
```python
new_item = await create_item(db, ...)
await db.commit()
await db.refresh(new_item)
```

### Read
```python
item = await get_item(db, id)
if item is None:
    raise not_found("Item not found")
```

### Update
```python
item = await get_item(db, id)
if item is None:
    raise not_found("Item not found")
    
updated = await update_item(db, id, ...)
await db.commit()
await db.refresh(updated)
```

### Delete
```python
item = await get_item(db, id)
if item is None:
    raise not_found("Item not found")
    
await delete_item(db, id)
await db.commit()
```

## Dependencies

CRUD modules depend on:
- `app.database.models` - SQLAlchemy ORM models
- `app.database.session` - Database session management
- `sqlalchemy.ext.asyncio` - Async SQLAlchemy

## Best Practices

1. **Keep functions focused**: One function per operation
2. **Use type hints**: Include parameter and return types
3. **Handle None cases**: Return None for not found, let routers handle errors
4. **Organization scoping**: Always filter by organization_name for multi-tenancy
5. **Async/await**: Use async functions consistently
6. **Document functions**: Include docstrings explaining parameters

## Adding New CRUD Operations

When adding new operations:

1. Import required models and session types
2. Use async functions with proper type hints
3. Filter by organization_name for multi-tenant operations
4. Return None for not found cases
5. Let routers handle commits and error responses

**Example:**
```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import MyModel

async def get_my_model(
    db: AsyncSession, 
    organization_name: str, 
    model_id: int
) -> MyModel | None:
    """Get model by ID within organization."""
    result = await db.execute(
        select(MyModel).where(
            MyModel.organization_name == organization_name,
            MyModel.id == model_id
        )
    )
    return result.scalar_one_or_none()
```
