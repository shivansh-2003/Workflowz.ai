# Routers

FastAPI route handlers for all API endpoints.

## Overview

This directory contains router modules that define all API endpoints. Each router handles a specific domain (authentication, projects, tasks, teams, superuser operations) and uses CRUD operations, dependencies, and schemas to implement the API.

## Files

### `auth.py`
Authentication endpoints for user registration and login.

**Endpoints:**
- `POST /api/auth/signup` - Public user registration (first user becomes superuser)
- `POST /api/auth/register` - Superuser-only user creation
- `POST /api/auth/token` - User login (OAuth2 password flow)

**Features:**
- JWT token generation on login
- Password hashing on registration
- First user automatically becomes superuser
- OAuth2 password flow implementation

**Usage:**
```bash
# Signup (public)
POST /api/auth/signup
{
  "email": "user@example.com",
  "password": "password123"
}

# Login
POST /api/auth/token
Content-Type: application/x-www-form-urlencoded
username=user@example.com&password=password123
```

### `superuser.py`
Superuser-only endpoints for organization management.

**Endpoints:**
- `GET /api/superuser/organizations/` - List all organizations
- `POST /api/superuser/organizations/` - Create organization
- `PATCH /api/superuser/organizations/{org_name}` - Rename organization
- `POST /api/superuser/organizations/{org_name}/head` - Change organization head

**Features:**
- Organization creation with head user assignment
- Organization listing with member counts
- Organization renaming
- Head user reassignment

**Permissions:** Superuser only

**Usage:**
```bash
# List organizations
GET /api/superuser/organizations/
Authorization: Bearer <superuser_token>

# Create organization
POST /api/superuser/organizations/
{
  "organization_name": "MyOrg",
  "head_email": "head@example.com",
  "head_name": "John Doe",
  "head_designation": "CTO"
}
```

### `teams.py`
Team member management endpoints.

**Endpoints:**
- `GET /api/teams` - List team members (org-scoped)
- `POST /api/teams` - Add team member
- `DELETE /api/teams/{member_id}` - Remove team member

**Features:**
- Organization-scoped team member listing
- Add members with user account requirement
- Remove members from organization

**Permissions:**
- View: All authenticated users in organization
- Add/Remove: Organization Head, Superuser

**Usage:**
```bash
# List members
GET /api/teams?organization_name=MyOrg

# Add member
POST /api/teams?organization_name=MyOrg
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "designation": "Developer",
  "position": "member"
}
```

### `projects.py`
Project management endpoints.

**Endpoints:**
- `GET /api/projects` - List projects (org-scoped)
- `POST /api/projects` - Create project
- `GET /api/projects/{project_id}` - Get project details
- `PATCH /api/projects/{project_id}` - Update project
- `DELETE /api/projects/{project_id}` - Delete project

**Features:**
- Organization-scoped project operations
- Automatic progress calculation
- Project CRUD operations

**Permissions:**
- View: All authenticated users in organization
- Create/Update/Delete: Organization Head, Superuser

**Usage:**
```bash
# List projects
GET /api/projects?organization_name=MyOrg

# Create project
POST /api/projects?organization_name=MyOrg
{
  "project_name": "New Project",
  "project_description": "Description"
}
```

### `tasks.py`
Task management endpoints.

**Endpoints:**
- `GET /api/tasks` - List tasks (project-scoped)
- `POST /api/tasks` - Create task
- `PATCH /api/tasks/{task_id}` - Update task
- `DELETE /api/tasks/{task_id}` - Delete task

**Features:**
- Project-scoped task operations
- Task assignment to team members
- Priority and deadline management
- Completion status tracking

**Permissions:**
- View: All authenticated users in organization
- Create/Update/Delete: Organization Head, Superuser
- Update completion: Assigned member, Organization Head, Superuser

**Usage:**
```bash
# List tasks
GET /api/tasks?organization_name=MyOrg&project_id=1

# Create task
POST /api/tasks?organization_name=MyOrg&project_id=1
{
  "task_description": "New task",
  "task_deadline": "2026-03-15",
  "task_assigned_to": 1,
  "task_importance": "high"
}
```

## Router Structure

Each router follows this pattern:

```python
from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from app.database.session import get_db

router = APIRouter()

@router.get("/endpoint")
async def my_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Endpoint logic
    return {"data": "result"}
```

## Common Patterns

### Organization Scoping
Most endpoints require `organization_name` query parameter:
```python
@router.get("/projects")
async def list_projects(
    organization_name: str,
    db: AsyncSession = Depends(get_db)
):
    projects = await get_projects(db, organization_name)
    return projects
```

### Role-Based Access
Use dependencies to enforce permissions:
```python
@router.post("/projects")
async def create_project(
    organization_name: str,
    current_user: User = Depends(get_current_head),
    db: AsyncSession = Depends(get_db)
):
    # Only organization heads can create projects
    pass
```

### Error Handling
Use custom exceptions for consistent errors:
```python
from app.core.exceptions import not_found

project = await get_project(db, org_name, project_id)
if project is None:
    raise not_found("Project not found")
```

### Response Models
Use Pydantic schemas for responses:
```python
from app.schemas.project import ProjectOut

@router.get("/projects/{project_id}", response_model=ProjectOut)
async def get_project(...):
    return project
```

## Router Registration

Routers are registered in `app/main.py`:

```python
from app.routers import auth, projects, tasks, teams, superuser

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(projects.router, prefix=settings.API_V1_PREFIX)
# etc.
```

## API Documentation

All endpoints are automatically documented:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

Documentation includes:
- Request/response schemas
- Parameter descriptions
- Authentication requirements
- Example requests

## Best Practices

1. **Use dependencies**: Leverage FastAPI dependencies for auth and DB
2. **Validate inputs**: Use Pydantic schemas for request validation
3. **Handle errors**: Use custom exceptions for consistent error responses
4. **Document endpoints**: Add docstrings and response models
5. **Organization scoping**: Always filter by organization_name
6. **Transaction management**: Commit changes in routers, not CRUD
7. **Response models**: Use Pydantic schemas for type-safe responses

## Adding New Endpoints

When adding a new endpoint:

1. Choose appropriate router file (or create new one)
2. Define endpoint function with proper dependencies
3. Use CRUD functions for database operations
4. Validate inputs with Pydantic schemas
5. Handle errors appropriately
6. Add response model if needed
7. Document with docstring

**Example:**
```python
@router.get("/custom", response_model=CustomOut)
async def custom_endpoint(
    organization_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Custom endpoint description."""
    data = await get_custom_data(db, organization_name)
    if not data:
        raise not_found("Data not found")
    return data
```
