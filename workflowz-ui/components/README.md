# Components

Reusable UI components for the Streamlit frontend.

## Overview

This directory contains reusable Streamlit components that are used across multiple pages to maintain consistency and reduce code duplication.

## Files

### `auth_forms.py`
Authentication-related forms for user login and registration.

**Functions:**
- `render_login_form()` - Displays login form with email/password inputs
- `render_signup_form()` - Displays signup form with validation

**Usage:**
```python
from components.auth_forms import render_login_form, render_signup_form

render_login_form()  # Display login form
render_signup_form()  # Display signup form
```

### `navigation.py`
Sidebar navigation component with user context and organization selection.

**Functions:**
- `render_sidebar()` - Renders the main sidebar with navigation links, user info, and organization input

**Features:**
- Displays user email and role
- Organization name input for superusers
- Navigation links to all pages
- Logout functionality

**Usage:**
```python
from components.navigation import render_sidebar

render_sidebar()  # Render sidebar on any page
```

### `progress_bars.py`
Progress visualization components for projects and tasks.

**Functions:**
- Progress bar rendering for project completion
- Visual indicators for task status

**Usage:**
```python
from components.progress_bars import render_progress_bar

render_progress_bar(progress_percentage)
```

## Design Principles

- **Reusability**: Components are designed to be used across multiple pages
- **Consistency**: Ensures UI consistency throughout the application
- **Separation of Concerns**: UI logic separated from page logic
- **State Management**: Components interact with Streamlit session state

## Adding New Components

When adding a new component:

1. Create a new `.py` file in this directory
2. Define functions that return Streamlit widgets or render UI
3. Document the component's purpose and usage
4. Import and use in pages as needed

**Example:**
```python
# components/my_component.py
import streamlit as st

def render_my_component(data):
    """Render a custom component.
    
    Args:
        data: Data to display in the component
    """
    st.write(f"Displaying: {data}")
```
