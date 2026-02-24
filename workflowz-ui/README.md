# Workflowz.ai Frontend (Streamlit)

Modern web interface for Workflowz.ai built with Streamlit, providing an intuitive UI for managing projects, tasks, and teams.

## 🎯 Overview

The Streamlit frontend provides a user-friendly interface for:
- User authentication (login/signup)
- Dashboard with project overview
- Project management (create, edit, delete)
- **AI Assistant** — generate task plans from project descriptions (Head/Superuser)
- Task management (assign, track, complete)
- Team management (view members, add/remove)
- Settings and user management

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Backend API running (see main README.md)
- Backend API accessible (default: `http://localhost:8000`)

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd workflowz-ui
   ```

2. **Create virtual environment** (optional)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API endpoint** (optional)
   
   Create `.env` file in `workflowz-ui/`:
   ```env
   API_BASE_URL=http://localhost:8000
   ```
   
   Or set environment variable:
   ```bash
   export API_BASE_URL="http://localhost:8000"
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```
   
   The UI will open at `http://localhost:8501`

## 📁 Project Structure

```
workflowz-ui/
├── app.py                      # Main entry point
├── components/                  # Reusable UI components
│   ├── auth_forms.py           # Login and signup forms
│   ├── navigation.py           # Sidebar navigation component
│   └── progress_bars.py        # Progress visualization
├── pages/                       # Streamlit pages
│   ├── 1_Dashboard.py          # Dashboard overview
│   ├── 2_Projects.py          # Project management
│   ├── 3_Tasks.py             # Task management
│   ├── 4_Team.py              # Team management
│   └── 5_Settings.py          # Settings and user management
├── services/                    # API client services
│   ├── api_client.py          # Base HTTP client with error handling
│   ├── auth_service.py        # Authentication API calls
│   ├── project_service.py     # Project API calls
│   ├── task_service.py        # Task API calls
│   ├── team_service.py       # Team API calls
│   ├── superuser_service.py  # Superuser API calls
│   └── ai_service.py         # AI workflow API calls
├── utils/                       # Utility functions
│   ├── config.py              # Configuration loading
│   ├── formatters.py          # Date and data formatting
│   ├── jwt.py                 # JWT token decoding
│   └── state.py               # Session state management
├── .streamlit/
│   └── config.toml            # Streamlit configuration
└── requirements.txt            # Python dependencies
```

## 🎨 Features

### Authentication
- **Login**: OAuth2 password flow with JWT tokens
- **Signup**: Public registration (first user becomes superuser)
- **Session Management**: Token stored in Streamlit session state
- **Auto-redirect**: Unauthenticated users redirected to login

### Pages

#### 1. Dashboard (`/`)
- Overview of all projects
- Task statistics
- Progress visualization
- Quick access to recent tasks

#### 2. Projects (`/Projects`)
- List all projects in organization
- Create new projects
- Edit project details
- Delete projects
- View project progress bars
- **AI Assistant** (Head/Superuser): Generate task plans, answer clarification questions, approve/reject and persist tasks

#### 3. Tasks (`/Tasks`)
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

#### 4. Team (`/Team`)
- View all team members
- Add new team members
- Remove team members
- View member details and assignments

#### 5. Settings (`/Settings`)
- View user profile
- **Superuser features**:
  - Create organizations
  - Rename organizations
  - Change organization head
  - Create user accounts
  - List all organizations

### Role-Based Access

The UI adapts based on user role:

- **Superuser**: 
  - Full access to all features
  - Organization name input in sidebar for org-scoped operations
  - Settings page with superuser controls

- **Organization Head**:
  - Can create/edit/delete projects
  - Can create/edit/delete tasks
  - Can manage team members
  - Limited to their organization

- **Member**:
  - Can view assigned tasks
  - Can mark tasks as complete/incomplete
  - Can view projects and team members
  - Limited to their organization

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in `workflowz-ui/` directory:

```env
API_BASE_URL=http://localhost:8000
```

Or set as system environment variable:
```bash
export API_BASE_URL="http://localhost:8000"
```

### Streamlit Configuration

Streamlit settings are in `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

## 🔧 Development

### Running in Development Mode

```bash
streamlit run app.py --server.runOnSave true
```

This enables auto-reload on file changes.

### Adding New Pages

1. Create a new file in `pages/` directory
2. Follow naming convention: `N_PageName.py` (number determines order)
3. Import required utilities:
   ```python
   from utils.state import require_auth, get_user_context
   from components.navigation import render_sidebar
   ```

### Adding New API Services

1. Create service file in `services/` directory
2. Use `APIClient` from `services.api_client`:
   ```python
   from services.api_client import APIClient
   
   def my_service_function():
       client = APIClient()
       response = client.get("/api/endpoint")
       return response.data
   ```

### State Management

Session state is managed in `utils/state.py`:
- `set_auth_session()` - Store auth token and user info
- `get_user_context()` - Get current user info
- `require_auth()` - Check if user is authenticated
- `clear_auth()` - Clear session and logout

## 🐛 Troubleshooting

### API Connection Issues

**Error: Connection refused**
- Ensure backend is running on the configured port
- Check `API_BASE_URL` environment variable
- Verify firewall/network settings

**Error: 401 Unauthorized**
- Token may have expired, try logging in again
- Check if backend `SECRET_KEY` matches
- Verify token is being sent in requests

### Date Formatting Errors

If you see `AttributeError: 'str' object has no attribute 'strftime'`:
- The `format_date()` function in `utils/formatters.py` handles this
- Ensure you're using the latest version of the formatter

### Organization Name Required

**Superuser sees "Organization name required"**
- Superusers must enter organization name in sidebar
- This is needed for org-scoped queries
- Enter the organization name in the sidebar input field

## 📦 Dependencies

See `requirements.txt` for full list. Key dependencies:

- `streamlit` - Web framework
- `httpx` - HTTP client for API calls
- `python-dotenv` - Environment variable management

## 🚢 Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your repository
4. Set environment variables:
   - `API_BASE_URL` - Your backend API URL
5. Deploy

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Environment Variables for Production

```env
API_BASE_URL=https://your-api-domain.com
```

## 📝 Notes

- The UI requires the backend API to be running and accessible
- JWT tokens are stored in Streamlit session state (not persistent across browser sessions)
- All API calls include authentication headers automatically
- Error handling is implemented in `api_client.py` for consistent error messages

## 🔗 Related Documentation

- [Main README](../README.md) - Full project documentation
- [Backend Setup Guide](../setup.md) - Backend setup instructions
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when backend is running)
