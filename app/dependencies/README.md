# Dependencies

FastAPI dependencies for authentication, authorization, and multi-tenancy.

## Overview

This directory contains FastAPI dependency functions that provide reusable authentication, authorization, and multi-tenancy functionality across router endpoints.

## Files

### `auth.py`
Authentication and authorization dependencies.

**Functions:**
- `get_current_user(token)` - Get current authenticated user from JWT token
- `get_current_superuser(current_user)` - Verify user is superuser
- `get_current_head(current_user, organization_name)` - Verify user is organization head
- `get_current_member(current_user, organization_name)` - Verify user is organization member

**Usage:**
```python
from app.dependencies.auth import get_current_user, get_current_superuser

@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_user)
):
    return {"user": current_user.email}

@router.get("/admin")
async def admin_endpoint(
    current_user: User = Depends(get_current_superuser)
):
    return {"message": "Admin access"}
```

**Token Extraction:**
- Tokens are extracted from `Authorization: Bearer <token>` header
- JWT tokens are verified and decoded
- User is fetched from database based on token subject (email)

**Role-Based Access:**
- `get_current_superuser` - Requires `is_superuser=True`
- `get_current_head` - Requires user to be head of specified organization
- `get_current_member` - Requires user to be member of specified organization

### `tenancy.py`
Multi-tenancy helpers for organization scoping.

**Functions:**
- `get_organization_name(...)` - Extract organization name from query params or user context
- Organization validation helpers

**Usage:**
```python
from app.dependencies.tenancy import get_organization_name

@router.get("/projects")
async def list_projects(
    organization_name: str = Depends(get_organization_name)
):
    projects = await get_projects(db, organization_name)
    return projects
```

**Purpose:**
- Ensures all operations are scoped to an organization
- Validates organization access permissions
- Provides consistent organization parameter handling

## Dependency Injection Pattern

FastAPI uses dependency injection to provide reusable functionality:

```python
from fastapi import Depends
from app.dependencies.auth import get_current_user

@router.get("/endpoint")
async def my_endpoint(
    current_user: User = Depends(get_current_user)
):
    # current_user is automatically provided by FastAPI
    # based on JWT token in request headers
    pass
```

## Common Patterns

### Protected Endpoint
Require authentication:
```python
@router.get("/protected")
async def protected(
    current_user: User = Depends(get_current_user)
):
    return {"user": current_user.email}
```

### Superuser Only
Require superuser role:
```python
@router.post("/admin")
async def admin_only(
    current_user: User = Depends(get_current_superuser)
):
    # Only superusers can access
    pass
```

### Organization Head
Require head role in organization:
```python
@router.post("/projects")
async def create_project(
    organization_name: str,
    current_user: User = Depends(get_current_head)
):
    # User must be head of organization_name
    pass
```

### Organization Scoped
Get organization from query params:
```python
@router.get("/projects")
async def list_projects(
    organization_name: str = Depends(get_organization_name)
):
    # organization_name extracted and validated
    projects = await get_projects(db, organization_name)
    return projects
```

## Error Handling

Dependencies raise HTTP exceptions for authentication/authorization failures:

- **401 Unauthorized**: Invalid or missing token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: User or organization not found

These exceptions are automatically handled by FastAPI and returned as JSON responses.

## Security Considerations

### Token Verification
- JWT tokens are verified using `SECRET_KEY`
- Token expiration is checked
- Invalid tokens result in 401 errors

### Role Verification
- Roles are verified against database
- Organization membership is checked
- Prevents privilege escalation

### Multi-Tenancy
- Organization access is validated
- Users can only access their organization's data
- Superusers can access all organizations

## Best Practices

1. **Use dependencies consistently**: Always use dependencies for auth, don't duplicate logic
2. **Chain dependencies**: Combine multiple dependencies when needed
3. **Handle errors**: Let dependencies raise exceptions, handle in error handlers if needed
4. **Document requirements**: Document which roles can access endpoints
5. **Test dependencies**: Write tests for dependency functions

## Adding New Dependencies

When adding a new dependency:

1. Create function with proper type hints
2. Use `Depends()` for sub-dependencies
3. Raise HTTP exceptions for failures
4. Document the dependency's purpose

**Example:**
```python
from fastapi import Depends, HTTPException, status
from app.dependencies.auth import get_current_user
from app.database.models import User

async def require_specific_role(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require user to have specific role."""
    if current_user.role != "specific_role":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user
```

## Dependencies Chain

Dependencies can depend on other dependencies:

```python
async def get_current_head(
    organization_name: str,
    current_user: User = Depends(get_current_user)
) -> User:
    # First get current user (from token)
    # Then verify they are head of organization
    pass
```

This allows building complex authorization logic from simpler building blocks.
