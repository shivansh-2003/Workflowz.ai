# Database

Database configuration, models, and session management.

## Overview

This directory contains all database-related code including SQLAlchemy ORM models, database session management, and database initialization.

## Structure

```
database/
├── models/          # SQLAlchemy ORM models
│   └── __init__.py  # Model definitions
└── session.py       # Database session management
```

## Files

### `session.py`
Database session management and connection setup.

**Components:**
- `get_db()` - FastAPI dependency for database sessions
- Database engine configuration
- Session factory setup

**Usage:**
```python
from app.database.session import get_db

@router.get("/endpoint")
async def my_endpoint(db: AsyncSession = Depends(get_db)):
    # Use db session
    result = await db.execute(select(User))
    return result.scalars().all()
```

**Features:**
- Async session support
- Automatic session cleanup
- Connection pooling
- Transaction management

### `models/__init__.py`
SQLAlchemy ORM model definitions for all database tables.

**Models:**

#### `User`
User accounts for authentication.

**Fields:**
- `id` (PK) - Auto-incrementing user ID
- `email` (UNIQUE) - User email address
- `hashed_password` - Bcrypt hashed password
- `is_superuser` - Boolean superuser flag
- `created_at` - Timestamp

**Relationships:**
- `team_members` - One-to-many with TeamMember

#### `TeamMember`
Team members within organizations.

**Fields:**
- `organization_name` (PK) - Organization identifier
- `member_id` (PK) - Auto-incrementing member ID
- `name` - Member name
- `email` - Member email
- `designation` - Job title/role
- `position` - 'head' or 'member'
- `user_id` (FK) - Reference to User
- `created_at` - Timestamp

**Constraints:**
- Unique constraint on `(organization_name, email)`
- Check constraint on `position` ('head' or 'member')

**Relationships:**
- `user` - Many-to-one with User

#### `Project`
Projects within organizations.

**Fields:**
- `organization_name` (PK) - Organization identifier
- `project_id` (PK) - Auto-incrementing project ID
- `project_name` - Project name
- `project_description` - Project description
- `project_progress` - Progress percentage (0-100)
- `created_by` - Email of creator
- `created_at` - Timestamp

**Constraints:**
- Unique constraint on `(organization_name, project_name)`
- Check constraint on `project_progress` (0-100)

#### `Task`
Tasks within projects.

**Fields:**
- `organization_name` (PK) - Organization identifier
- `project_id` (PK, FK) - Project reference
- `task_id` (PK) - Auto-incrementing task ID
- `task_description` - Task description
- `task_deadline` - Optional deadline date
- `task_assigned_to` (FK) - Team member reference
- `task_importance` - 'high', 'medium', 'low', or NULL
- `task_completed` - Boolean completion status
- `created_at` - Timestamp

**Constraints:**
- Foreign key to `projects(organization_name, project_id)`
- Foreign key to `teams(organization_name, member_id)`
- Check constraint on `task_importance`

## Database Schema Design

### Multi-Tenancy
- All tables include `organization_name` in primary/composite keys
- Ensures data isolation between organizations
- Queries must always filter by `organization_name`

### Relationships
```
User (1) ──< (many) TeamMember
TeamMember (1) ──< (many) Task (via task_assigned_to)
Project (1) ──< (many) Task (via project_id)
```

### Composite Primary Keys
- `teams`: `(organization_name, member_id)`
- `projects`: `(organization_name, project_id)`
- `tasks`: `(organization_name, project_id, task_id)`

This design ensures:
- Data isolation per organization
- Auto-incrementing IDs scoped per organization
- Foreign key relationships maintain organization context

## Session Management

### Async Sessions
The application uses SQLAlchemy's async engine and sessions:
```python
from sqlalchemy.ext.asyncio import AsyncSession

async def my_function(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()
```

### Dependency Injection
FastAPI dependencies provide database sessions:
```python
from app.database.session import get_db

@router.get("/endpoint")
async def endpoint(db: AsyncSession = Depends(get_db)):
    # db session is automatically provided
    pass
```

### Transaction Management
- Commits are handled in router endpoints
- Sessions are automatically closed after request
- Rollback on exceptions

## Migrations

Database migrations are managed by Alembic:
- Migration files: `alembic/versions/`
- Configuration: `alembic.ini`, `alembic/env.py`
- Commands:
  - `alembic upgrade head` - Apply migrations
  - `alembic revision --autogenerate -m "message"` - Create migration

## Connection String

Database connection is configured via `DATABASE_URL` environment variable:
```
postgresql+asyncpg://user:password@host:port/database
```

**Note:** Must use `asyncpg` driver for async operations.

## Best Practices

1. **Always filter by organization**: Include `organization_name` in queries
2. **Use async sessions**: All database operations should be async
3. **Handle None cases**: Check for None when fetching single records
4. **Commit in routers**: Handle commits at the router level, not in CRUD
5. **Use relationships**: Leverage SQLAlchemy relationships for related data
6. **Index frequently queried fields**: Email, organization_name, etc.

## Adding New Models

When adding a new model:

1. Define model class in `models/__init__.py`
2. Include `organization_name` if multi-tenant
3. Define relationships with other models
4. Add constraints (unique, check, foreign keys)
5. Create Alembic migration: `alembic revision --autogenerate`

**Example:**
```python
class MyModel(Base):
    __tablename__ = "my_table"
    
    organization_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    __table_args__ = (
        UniqueConstraint("organization_name", "name"),
    )
```
