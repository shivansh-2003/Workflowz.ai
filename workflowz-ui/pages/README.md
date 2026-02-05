# Pages

Streamlit pages that make up the main application interface.

## Overview

This directory contains the main pages of the Workflowz.ai application. Streamlit automatically detects files in this directory and creates navigation routes based on the filename prefix (number) and name.

## Page Files

### `1_Dashboard.py`
Main dashboard page providing an overview of projects and tasks.

**Features:**
- Project overview with progress bars
- Task statistics
- Quick access to recent activities
- Visual progress indicators

**Route:** `/` (home page)

### `2_Projects.py`
Project management page for creating, viewing, editing, and deleting projects.

**Features:**
- List all projects in the organization
- Create new projects
- Edit project details (name, description)
- Delete projects
- View project progress
- Filter and search projects

**Route:** `/Projects`

**Permissions:**
- View: All authenticated users
- Create/Edit/Delete: Organization Head, Superuser

### `3_Tasks.py`
Task management page for creating, assigning, and tracking tasks.

**Features:**
- Filter tasks by project
- Create tasks with:
  - Description
  - Priority (high/medium/low)
  - Deadline
  - Assignment to team members
- Mark tasks as complete/incomplete
- Edit task details
- Delete tasks
- View task list with status indicators

**Route:** `/Tasks`

**Permissions:**
- View: All authenticated users
- Create/Edit/Delete: Organization Head, Superuser
- Update completion status: Assigned member, Organization Head, Superuser

### `4_Team.py`
Team management page for viewing and managing team members.

**Features:**
- View all team members in organization
- Add new team members
- Remove team members
- View member details (name, email, designation)
- See member assignments

**Route:** `/Team`

**Permissions:**
- View: All authenticated users
- Add/Remove: Organization Head, Superuser

### `5_Settings.py`
Settings page for user profile and administrative controls.

**Features:**
- User profile display
- **Superuser Controls:**
  - Create organizations
  - Rename organizations
  - Change organization head
  - Create user accounts
  - List all organizations

**Route:** `/Settings`

**Permissions:**
- Profile view: All authenticated users
- Superuser controls: Superuser only

## Page Structure

Each page typically follows this structure:

```python
import streamlit as st
from components.navigation import render_sidebar
from utils.state import require_auth, get_user_context

# Page configuration
st.set_page_config(page_title="Page Name", page_icon="📄")

# Authentication check
if not require_auth():
    st.switch_page("app.py")

# Render sidebar
render_sidebar()

# Get user context
user = get_user_context() or {}
role = user.get("role")

# Page content
st.title("Page Title")
# ... page-specific content ...
```

## Page Naming Convention

Pages are numbered to control navigation order:
- `1_Dashboard.py` - First in navigation
- `2_Projects.py` - Second
- `3_Tasks.py` - Third
- etc.

The number prefix determines the order in Streamlit's sidebar navigation.

## Common Patterns

### Authentication
All pages should check authentication:
```python
if not require_auth():
    st.switch_page("app.py")
```

### Organization Scoping
For org-scoped operations, get organization name:
```python
org_name = st.session_state.get("organization_name")
if not org_name and role == "superuser":
    st.warning("Please enter organization name in sidebar")
    st.stop()
```

### Error Handling
Wrap API calls in try-except:
```python
try:
    data = some_service_function()
except Exception as exc:
    st.error(f"Error: {exc}")
```

### State Management
Use session state for temporary data:
```python
if "key" not in st.session_state:
    st.session_state["key"] = default_value
```

## Adding New Pages

1. Create a new file: `N_PageName.py` (where N is the next number)
2. Follow the page structure pattern above
3. Import required components and utilities
4. Implement authentication checks
5. Add navigation link in `components/navigation.py` if needed

## Dependencies

Pages depend on:
- `components/` - UI components
- `services/` - API client services
- `utils/` - Utility functions and state management
