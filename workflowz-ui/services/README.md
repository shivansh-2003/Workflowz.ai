# Services

API client services for communicating with the FastAPI backend.

## Overview

This directory contains service modules that handle all API communication between the Streamlit frontend and the FastAPI backend. Each service module provides functions for interacting with specific API endpoints.

## Files

### `api_client.py`
Base HTTP client with error handling and authentication.

**Classes:**
- `APIClient` - Main HTTP client class

**Features:**
- Automatic JWT token injection from session state
- Error handling and exception raising
- Response parsing
- Base URL configuration

**Usage:**
```python
from services.api_client import APIClient

client = APIClient()
response = client.get("/api/endpoint")
data = response.data
```

**Methods:**
- `get(url, params=None)` - GET request
- `post(url, json=None, data=None, params=None)` - POST request
- `patch(url, json=None)` - PATCH request
- `delete(url)` - DELETE request

### `auth_service.py`
Authentication-related API calls.

**Functions:**
- `login(email, password)` - Authenticate user and get JWT token
- `signup(email, password)` - Register new user (public endpoint)
- `register_user(email, password, is_superuser)` - Create user (superuser only)

**Endpoints Used:**
- `POST /api/auth/token` - Login
- `POST /api/auth/signup` - Public signup
- `POST /api/auth/register` - Superuser user creation

**Usage:**
```python
from services.auth_service import login, signup

token = login("user@example.com", "password")
user_data = signup("newuser@example.com", "password")
```

### `project_service.py`
Project management API calls.

**Functions:**
- `list_projects(org_name)` - Get all projects in organization
- `get_project(project_id, org_name)` - Get project details
- `create_project(payload, org_name)` - Create new project
- `update_project(project_id, payload, org_name)` - Update project
- `delete_project(project_id, org_name)` - Delete project

**Endpoints Used:**
- `GET /api/projects` - List projects
- `GET /api/projects/{project_id}` - Get project
- `POST /api/projects` - Create project
- `PATCH /api/projects/{project_id}` - Update project
- `DELETE /api/projects/{project_id}` - Delete project

**Usage:**
```python
from services.project_service import list_projects, create_project

projects = list_projects("my-org")
new_project = create_project({"project_name": "New Project"}, "my-org")
```

### `task_service.py`
Task management API calls.

**Functions:**
- `list_tasks(project_id, org_name)` - Get all tasks in project
- `create_task(project_id, payload, org_name)` - Create new task
- `update_task(project_id, task_id, payload, org_name)` - Update task
- `delete_task(project_id, task_id, org_name)` - Delete task
- `complete_task(project_id, task_id, completed, org_name)` - Toggle task completion

**Endpoints Used:**
- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create task
- `PATCH /api/tasks/{task_id}` - Update task
- `DELETE /api/tasks/{task_id}` - Delete task

**Usage:**
```python
from services.task_service import list_tasks, create_task

tasks = list_tasks(project_id=1, org_name="my-org")
new_task = create_task(1, {"task_description": "New task"}, "my-org")
```

### `team_service.py`
Team management API calls.

**Functions:**
- `list_members(org_name)` - Get all team members
- `add_member(payload, org_name)` - Add team member
- `remove_member(member_id, org_name)` - Remove team member

**Endpoints Used:**
- `GET /api/teams` - List team members
- `POST /api/teams` - Add team member
- `DELETE /api/teams/{member_id}` - Remove team member

**Usage:**
```python
from services.team_service import list_members, add_member

members = list_members("my-org")
add_member({"name": "John", "email": "john@example.com"}, "my-org")
```

### `superuser_service.py`
Superuser-specific API calls.

**Functions:**
- `list_organizations()` - Get all organizations
- `create_organization(payload)` - Create organization
- `rename_organization(org_name, new_name)` - Rename organization
- `change_organization_head(org_name, new_head_email)` - Change organization head

**Endpoints Used:**
- `GET /api/superuser/organizations/` - List organizations
- `POST /api/superuser/organizations/` - Create organization
- `PATCH /api/superuser/organizations/{org_name}` - Rename organization
- `POST /api/superuser/organizations/{org_name}/head` - Change head

**Usage:**
```python
from services.superuser_service import list_organizations, create_organization

orgs = list_organizations()
create_organization({"organization_name": "NewOrg", "head_email": "head@example.com"})
```

## Design Patterns

### Error Handling
All services use `APIClient` which handles errors consistently:
- HTTP errors are caught and raised as `ApiError`
- Error details are extracted from API responses
- Consistent error messages across the application

### Authentication
- JWT tokens are automatically injected by `APIClient`
- Tokens are retrieved from Streamlit session state
- No manual token management needed in service functions

### Organization Scoping
- Most endpoints require `organization_name` parameter
- Services accept `org_name` parameter and pass it as query param
- Ensures multi-tenancy isolation

## Adding New Services

When adding a new service:

1. Create a new `.py` file in this directory
2. Import `APIClient`:
   ```python
   from services.api_client import APIClient
   ```

3. Define service functions:
   ```python
   def my_service_function(param1, org_name):
       client = APIClient()
       response = client.get("/api/endpoint", params={"org": org_name})
       return response.data
   ```

4. Document the function with docstrings
5. Handle errors appropriately (APIClient raises exceptions)

## Dependencies

Services depend on:
- `utils/config.py` - API base URL configuration
- `utils/state.py` - Session state for JWT tokens

## Best Practices

1. **Keep functions focused**: One function per API endpoint
2. **Use type hints**: Help with IDE autocomplete and type checking
3. **Document parameters**: Include docstrings explaining parameters
4. **Handle edge cases**: Check for None values, empty responses
5. **Consistent naming**: Use clear, descriptive function names
