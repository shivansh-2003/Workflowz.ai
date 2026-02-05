# Models

SQLAlchemy ORM model definitions.

## Overview

This directory contains the SQLAlchemy ORM model definitions that map to database tables. All models are defined in `__init__.py` and represent the core data structures of the application.

## Models

### `User`
Represents user accounts for authentication.

**Table:** `users`

**Fields:**
- `id` (Integer, PK) - Auto-incrementing user ID
- `email` (String(100), UNIQUE) - User email address
- `hashed_password` (String(255)) - Bcrypt hashed password
- `is_superuser` (Boolean) - Superuser flag
- `created_at` (DateTime) - Creation timestamp

**Relationships:**
- `team_members` - One-to-many relationship with TeamMember

**Usage:**
```python
from app.database.models import User

user = User(
    email="user@example.com",
    hashed_password="hashed_password",
    is_superuser=False
)
```

### `TeamMember`
Represents team members within organizations.

**Table:** `teams`

**Fields:**
- `organization_name` (String(100), PK) - Organization identifier
- `member_id` (Integer, PK) - Auto-incrementing member ID
- `name` (String(100)) - Member name
- `email` (String(100)) - Member email
- `designation` (String(100), Optional) - Job title/role
- `position` (String(50)) - 'head' or 'member'
- `user_id` (Integer, FK → users.id) - Reference to User
- `created_at` (DateTime) - Creation timestamp

**Constraints:**
- Unique constraint on `(organization_name, email)`
- Check constraint: `position IN ('head', 'member')`

**Relationships:**
- `user` - Many-to-one relationship with User

**Usage:**
```python
from app.database.models import TeamMember

member = TeamMember(
    organization_name="MyOrg",
    name="John Doe",
    email="john@example.com",
    designation="Developer",
    position="member",
    user_id=1
)
```

### `Project`
Represents projects within organizations.

**Table:** `projects`

**Fields:**
- `organization_name` (String(100), PK) - Organization identifier
- `project_id` (Integer, PK) - Auto-incrementing project ID
- `project_name` (String(100)) - Project name
- `project_description` (Text, Optional) - Project description
- `project_progress` (Integer) - Progress percentage (0-100)
- `created_by` (String(100)) - Email of creator
- `created_at` (DateTime) - Creation timestamp

**Constraints:**
- Unique constraint on `(organization_name, project_name)`
- Check constraint: `project_progress BETWEEN 0 AND 100`

**Usage:**
```python
from app.database.models import Project

project = Project(
    organization_name="MyOrg",
    project_name="New Project",
    project_description="Description",
    project_progress=0,
    created_by="creator@example.com"
)
```

### `Task`
Represents tasks within projects.

**Table:** `tasks`

**Fields:**
- `organization_name` (String(100), PK) - Organization identifier
- `project_id` (Integer, PK, FK) - Project reference
- `task_id` (Integer, PK) - Auto-incrementing task ID
- `task_description` (Text) - Task description
- `task_deadline` (Date, Optional) - Deadline date
- `task_assigned_to` (Integer, FK) - Team member reference
- `task_importance` (String(50), Optional) - 'high', 'medium', 'low', or NULL
- `task_completed` (Boolean) - Completion status
- `created_at` (DateTime) - Creation timestamp

**Constraints:**
- Foreign key to `projects(organization_name, project_id)` ON DELETE CASCADE
- Foreign key to `teams(organization_name, member_id)` ON DELETE RESTRICT
- Check constraint: `task_importance IN ('high', 'medium', 'low') OR task_importance IS NULL`

**Usage:**
```python
from app.database.models import Task
from datetime import date

task = Task(
    organization_name="MyOrg",
    project_id=1,
    task_description="Complete task",
    task_deadline=date(2026, 3, 15),
    task_assigned_to=1,
    task_importance="high",
    task_completed=False
)
```

## Model Relationships

```
User (1) ──< (many) TeamMember
                │
                └──< (many) Task (via task_assigned_to)

Project (1) ──< (many) Task (via project_id)
```

## Design Principles

### Multi-Tenancy
All models (except User) include `organization_name` in their primary key to ensure data isolation between organizations.

### Composite Primary Keys
- `TeamMember`: `(organization_name, member_id)`
- `Project`: `(organization_name, project_id)`
- `Task`: `(organization_name, project_id, task_id)`

This design allows:
- Auto-incrementing IDs scoped per organization
- Data isolation between organizations
- Foreign key relationships maintain organization context

### Relationships
SQLAlchemy relationships are defined using `relationship()`:
- One-to-many: `relationship("Model", back_populates="field")`
- Many-to-one: `ForeignKey("table.column")` + `relationship()`

## Usage in CRUD Operations

Models are used in CRUD operations:

```python
from app.database.models import User
from sqlalchemy import select

# Query
result = await db.execute(select(User).where(User.email == email))
user = result.scalar_one_or_none()

# Create
user = User(email=email, hashed_password=hashed)
db.add(user)
await db.commit()

# Update
user.email = new_email
await db.commit()

# Delete
await db.delete(user)
await db.commit()
```

## Model Validation

While Pydantic schemas handle API validation, SQLAlchemy models enforce:
- Database-level constraints (unique, check, foreign keys)
- Type constraints (String length, Integer ranges)
- Relationship integrity

## Best Practices

1. **Always include organization_name**: For multi-tenant models
2. **Use relationships**: Leverage SQLAlchemy relationships for related data
3. **Define constraints**: Use table_args for constraints
4. **Type hints**: Use Mapped[] for type hints
5. **Index frequently queried fields**: Email, organization_name, etc.
6. **Document relationships**: Use relationship() with clear back_populates

## Adding New Models

When adding a new model:

1. Define class inheriting from `Base`
2. Set `__tablename__`
3. Define fields with `Mapped[]` type hints
4. Add primary key(s)
5. Define relationships if needed
6. Add constraints in `__table_args__`
7. Create Alembic migration

**Example:**
```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class MyModel(Base):
    __tablename__ = "my_table"
    
    organization_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    __table_args__ = (
        UniqueConstraint("organization_name", "name"),
    )
```

## Migration Considerations

When modifying models:
1. Update model definition
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review migration file
4. Apply migration: `alembic upgrade head`

**Note:** Be careful with:
- Column deletions (data loss)
- Constraint changes (may fail if data violates constraints)
- Foreign key changes (may break relationships)
