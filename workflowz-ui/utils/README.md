# Utils

Utility functions and helpers used throughout the Streamlit frontend.

## Overview

This directory contains utility modules that provide common functionality used across multiple pages and components. These utilities handle configuration, formatting, authentication state, and other shared operations.

## Files

### `config.py`
Configuration management for loading environment variables and settings.

**Functions:**
- `get_api_base_url()` - Get the API base URL from environment or default

**Usage:**
```python
from utils.config import get_api_base_url

api_url = get_api_base_url()  # Returns API_BASE_URL env var or default
```

**Environment Variables:**
- `API_BASE_URL` - Backend API base URL (default: `http://localhost:8000`)

### `formatters.py`
Data formatting utilities for dates, numbers, and other data types.

**Functions:**
- `format_date(value)` - Format date/datetime/string to YYYY-MM-DD format

**Features:**
- Handles None values (returns "-")
- Supports date, datetime, and string inputs
- Parses ISO format strings
- Returns formatted date strings

**Usage:**
```python
from utils.formatters import format_date

formatted = format_date("2026-03-15")  # Returns "2026-03-15"
formatted = format_date(None)  # Returns "-"
formatted = format_date(datetime.now())  # Returns formatted date
```

### `jwt.py`
JWT token decoding utilities for client-side token inspection.

**Functions:**
- `decode_jwt(token)` - Decode JWT token without verification (client-side only)

**Features:**
- Extracts payload from JWT token
- Used for reading user info from token
- **Note**: Does not verify signature (client-side only)

**Usage:**
```python
from utils.jwt import decode_jwt

payload = decode_jwt(token)
user_email = payload.get("sub")
user_role = payload.get("role")
```

**Security Note:**
This function is for client-side token reading only. Token verification is handled by the backend.

### `state.py`
Streamlit session state management for authentication and user context.

**Functions:**
- `init_state()` - Initialize session state variables
- `require_auth()` - Check if user is authenticated
- `get_user_context()` - Get current user information from token
- `set_auth_session(token)` - Store authentication token and user context
- `clear_auth()` - Clear authentication and logout user

**Session State Variables:**
- `access_token` - JWT authentication token
- `user_email` - Current user's email
- `user_role` - Current user's role (superuser/head/member)
- `organization_name` - Selected organization (for superusers)

**Usage:**
```python
from utils.state import require_auth, get_user_context, set_auth_session

# Check authentication
if not require_auth():
    st.switch_page("app.py")

# Get user info
user = get_user_context()
email = user.get("email")
role = user.get("role")

# Set authentication after login
set_auth_session(token)
```

## Common Patterns

### Authentication Check
Used at the start of protected pages:
```python
from utils.state import require_auth

if not require_auth():
    st.switch_page("app.py")
```

### User Context
Get current user information:
```python
from utils.state import get_user_context

user = get_user_context() or {}
role = user.get("role")
email = user.get("email")
```

### Date Formatting
Format dates for display:
```python
from utils.formatters import format_date

deadline = task.get("task_deadline")
st.write(f"Deadline: {format_date(deadline)}")
```

## Adding New Utilities

When adding a new utility module:

1. Create a new `.py` file in this directory
2. Define utility functions with clear names
3. Add docstrings explaining purpose and usage
4. Import and use in pages/components as needed

**Example:**
```python
# utils/my_util.py

def format_currency(amount):
    """Format number as currency.
    
    Args:
        amount: Numeric amount to format
        
    Returns:
        Formatted currency string
    """
    return f"${amount:,.2f}"
```

## Dependencies

Utils depend on:
- `python-dotenv` - Environment variable loading
- `jose` (via jwt.py) - JWT token decoding
- Streamlit session state

## Best Practices

1. **Keep utilities pure**: Functions should not have side effects when possible
2. **Handle edge cases**: Check for None, empty values, etc.
3. **Document functions**: Include docstrings with parameter descriptions
4. **Type hints**: Use type hints for better IDE support
5. **Error handling**: Handle exceptions gracefully
