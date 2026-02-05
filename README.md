# Workflowz.ai

A comprehensive project management platform built with FastAPI backend and Streamlit frontend, designed to help teams organize, track, and manage projects, tasks, and team members with role-based access control and multi-tenancy support.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Frontend Usage](#frontend-usage)
- [Database Schema](#database-schema)
- [Sample Data](#sample-data)
- [Development](#development)
- [Deployment](#deployment)

## 🎯 Overview

Workflowz.ai is a project management tool that enables teams to:
- **Organize work** by companies/organizations with isolated workspaces
- **Manage teams** with clear roles (Superuser, Organization Head, Member)
- **Track projects** with automatic progress calculation based on task completion
- **Assign tasks** with priorities, deadlines, and status tracking
- **Collaborate** across multiple projects within an organization

The platform uses **multi-tenancy** to ensure data isolation between organizations and implements **RBAC (Role-Based Access Control)** to manage permissions at different levels.

## ✨ Features

### Authentication & Authorization
- JWT-based authentication with OAuth2 password flow
- Role-based access control (Superuser, Organization Head, Member)
- Secure password hashing using bcrypt
- Token-based session management

### Multi-Tenancy
- Organization-scoped data isolation
- Each organization operates independently
- Superuser can manage multiple organizations

### Project Management
- Create and manage projects within organizations
- Automatic project progress calculation (0-100%)
- Project descriptions and metadata
- Created-by tracking

### Task Management
- Create, update, and delete tasks
- Assign tasks to team members
- Set priorities (high, medium, low)
- Set deadlines and track completion status
- Task filtering and organization

### Team Management
- Add/remove team members
- Assign roles (head/member)
- Track member designations
- View team composition

### User Interface
- Modern Streamlit-based web interface
- Responsive design
- Real-time updates
- Intuitive navigation

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy 2.x** - Async ORM for database operations
- **PostgreSQL** - Relational database
- **Alembic** - Database migrations
- **Pydantic** - Data validation and serialization
- **JWT (python-jose)** - Token-based authentication
- **Passlib[bcrypt]** - Password hashing
- **AsyncPG** - Async PostgreSQL driver

### Frontend
- **Streamlit** - Python web app framework
- **httpx** - Async HTTP client for API calls
- **python-dotenv** - Environment variable management

## 🏗 Architecture

```
┌─────────────────┐
│  Streamlit UI   │  (Frontend - workflowz-ui/)
│   (Port 8501)   │
└────────┬────────┘
         │ HTTP/REST API
         │ (JWT Auth)
┌────────▼────────┐
│   FastAPI       │  (Backend - app/)
│   (Port 8000)   │
└────────┬────────┘
         │ SQLAlchemy ORM
         │ (Async)
┌────────▼────────┐
│   PostgreSQL     │  (Database)
└─────────────────┘
```

### Key Components

1. **Backend API** (`app/`)
   - RESTful API endpoints
   - Authentication & authorization
   - CRUD operations
   - Business logic

2. **Frontend UI** (`workflowz-ui/`)
   - Streamlit pages for different views
   - API client services
   - State management
   - User interface components

3. **Database**
   - PostgreSQL with async operations
   - Alembic for migrations
   - Multi-tenant schema design

## 📁 Project Structure

```
workflowz_ai/
├── app/                          # FastAPI backend
│   ├── core/                     # Core configuration
│   │   ├── config.py             # Settings and environment variables
│   │   ├── security.py           # Password hashing, JWT tokens
│   │   └── exceptions.py        # Custom exceptions
│   ├── database/                 # Database setup
│   │   ├── models/              # SQLAlchemy ORM models
│   │   └── session.py           # Database session management
│   ├── crud/                     # Database operations
│   │   ├── user.py
│   │   ├── team.py
│   │   ├── project.py
│   │   └── task.py
│   ├── routers/                  # API route handlers
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── superuser.py         # Superuser operations
│   │   ├── teams.py             # Team management
│   │   ├── projects.py         # Project CRUD
│   │   └── tasks.py             # Task CRUD
│   ├── schemas/                  # Pydantic models
│   │   ├── auth.py
│   │   ├── organization.py
│   │   ├── team.py
│   │   ├── project.py
│   │   └── task.py
│   ├── dependencies/             # FastAPI dependencies
│   │   ├── auth.py              # Auth dependencies
│   │   └── tenancy.py           # Multi-tenancy helpers
│   └── main.py                  # FastAPI app entry point
│
├── workflowz-ui/                 # Streamlit frontend
│   ├── app.py                   # Main entry point
│   ├── components/              # Reusable UI components
│   │   ├── auth_forms.py       # Login/signup forms
│   │   ├── navigation.py        # Sidebar navigation
│   │   └── progress_bars.py    # Progress visualization
│   ├── pages/                   # Streamlit pages
│   │   ├── 1_Dashboard.py
│   │   ├── 2_Projects.py
│   │   ├── 3_Tasks.py
│   │   ├── 4_Team.py
│   │   └── 5_Settings.py
│   ├── services/                # API client services
│   │   ├── api_client.py       # Base HTTP client
│   │   ├── auth_service.py
│   │   ├── project_service.py
│   │   ├── task_service.py
│   │   ├── team_service.py
│   │   └── superuser_service.py
│   └── utils/                   # Utility functions
│       ├── config.py
│       ├── formatters.py
│       ├── jwt.py
│       └── state.py
│
├── alembic/                     # Database migrations
│   ├── versions/
│   └── env.py
│
├── requirements.txt             # Backend dependencies
├── .env.example                 # Environment variables template
├── setup.md                     # Detailed setup guide
└── README.md                    # This file
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.11+ (recommended)
- PostgreSQL 14+ (or use Supabase/cloud PostgreSQL)
- `pip` package manager

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd workflowz_ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/workflowz
   SECRET_KEY=your-secret-key-here-change-this
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days
   ```

5. **Set up PostgreSQL database**
   ```sql
   CREATE USER workflowz_user WITH PASSWORD 'your_password';
   CREATE DATABASE workflowz OWNER workflowz_user;
   GRANT ALL PRIVILEGES ON DATABASE workflowz TO workflowz_user;
   ```

   **Or use Supabase:**
   - Create a project on [Supabase](https://supabase.com)
   - Get the connection string from Project Settings → Database
   - Use format: `postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres`

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start the backend server**
   ```bash
   uvicorn app.main:app --reload
   ```
   
   The API will be available at `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

### Frontend Setup

1. **Navigate to UI directory**
   ```bash
   cd workflowz-ui
   ```

2. **Create virtual environment** (optional, can use same as backend)
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API endpoint** (if different from default)
   Create `.env` file in `workflowz-ui/`:
   ```env
   API_BASE_URL=http://localhost:8000
   ```

5. **Start the Streamlit app**
   ```bash
   streamlit run app.py
   ```
   
   The UI will be available at `http://localhost:8501`

### Quick Start

1. **First user registration**
   - Open the Streamlit UI at `http://localhost:8501`
   - Click "Sign up" tab
   - Register with your email and password
   - The first user automatically becomes a superuser

2. **Create an organization**
   - Log in as superuser
   - Go to Settings page
   - Use "Create organization" form
   - Note: Head user must exist before creating organization

3. **Add team members**
   - Go to Settings → Create user (to create user accounts)
   - Go to Team page → Add member (to add them to organization)

4. **Create projects and tasks**
   - Go to Projects page → Create project
   - Go to Tasks page → Select project → Create task

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

### Endpoints Overview

#### Authentication (`/api/auth`)
- `POST /api/auth/signup` - Public user registration (first user becomes superuser)
- `POST /api/auth/register` - Superuser-only user creation
- `POST /api/auth/token` - Login (OAuth2 password flow)

#### Superuser (`/api/superuser`)
- `GET /api/superuser/organizations/` - List all organizations
- `POST /api/superuser/organizations/` - Create organization
- `PATCH /api/superuser/organizations/{org_name}` - Rename organization
- `POST /api/superuser/organizations/{org_name}/head` - Change organization head

#### Teams (`/api/teams`)
- `GET /api/teams` - List team members (org-scoped)
- `POST /api/teams` - Add team member
- `DELETE /api/teams/{member_id}` - Remove team member

#### Projects (`/api/projects`)
- `GET /api/projects` - List projects (org-scoped)
- `POST /api/projects` - Create project
- `GET /api/projects/{project_id}` - Get project details
- `PATCH /api/projects/{project_id}` - Update project
- `DELETE /api/projects/{project_id}` - Delete project

#### Tasks (`/api/tasks`)
- `GET /api/tasks` - List tasks (project-scoped)
- `POST /api/tasks` - Create task
- `PATCH /api/tasks/{task_id}` - Update task
- `DELETE /api/tasks/{task_id}` - Delete task

### Interactive API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🖥 Frontend Usage

### Pages

1. **Dashboard** (`/`)
   - Overview of projects and tasks
   - Progress visualization
   - Quick stats

2. **Projects** (`/Projects`)
   - List all projects in organization
   - Create/edit/delete projects
   - View project progress

3. **Tasks** (`/Tasks`)
   - Filter tasks by project
   - Create/edit/delete tasks
   - Mark tasks as complete
   - View task details

4. **Team** (`/Team`)
   - View team members
   - Add/remove members
   - View member details

5. **Settings** (`/Settings`)
   - User profile
   - Superuser controls (if applicable)
   - Organization management
   - User creation

### Role-Based Access

- **Superuser**: Full access to all features, can manage organizations
- **Organization Head**: Can manage projects and tasks within their organization
- **Member**: Can view and update tasks assigned to them

## 🗄 Database Schema

### Tables

#### `users`
- `id` (PK) - Auto-incrementing user ID
- `email` (UNIQUE) - User email address
- `hashed_password` - Bcrypt hashed password
- `is_superuser` - Boolean flag for superuser status
- `created_at` - Timestamp

#### `teams`
- `organization_name` (PK) - Organization identifier
- `member_id` (PK) - Auto-incrementing member ID
- `name` - Member name
- `email` - Member email
- `designation` - Job title/role
- `position` - 'head' or 'member'
- `user_id` (FK → users.id) - Reference to user account
- `created_at` - Timestamp

#### `projects`
- `organization_name` (PK) - Organization identifier
- `project_id` (PK) - Auto-incrementing project ID
- `project_name` - Project name
- `project_description` - Project description
- `project_progress` - Progress percentage (0-100)
- `created_by` - Email of creator
- `created_at` - Timestamp

#### `tasks`
- `organization_name` (PK) - Organization identifier
- `project_id` (PK, FK → projects) - Project reference
- `task_id` (PK) - Auto-incrementing task ID
- `task_description` - Task description
- `task_deadline` - Optional deadline date
- `task_assigned_to` (FK → teams.member_id) - Assigned team member
- `task_importance` - 'high', 'medium', 'low', or NULL
- `task_completed` - Boolean completion status
- `created_at` - Timestamp

### Relationships

- Users → Team Members (1:many)
- Organizations → Projects (1:many via `organization_name`)
- Projects → Tasks (1:many via composite key)
- Team Members → Tasks (1:many via `task_assigned_to`)

## 📊 Sample Data

SQL files are provided for populating the database with sample data:

1. **`insert_users.sql`** - Creates 10 sample users
   - All users have password: `password123`
   - Run this first

2. **`insert_projects_and_tasks.sql`** - Creates:
   - Team members for organization `bajaj-finserv`
   - 2 projects (E-Commerce Platform, Mobile Banking App)
   - 37 tasks across both projects

**To use:**
```bash
# Option 1: Using psql
psql -d your_database -f insert_users.sql
psql -d your_database -f insert_projects_and_tasks.sql

# Option 2: Copy SQL into Supabase SQL Editor
```

## 🔧 Development

### Running Tests

```bash
# Backend tests (if implemented)
pytest app/tests/

# Frontend tests (if implemented)
pytest workflowz-ui/tests/
```

### Code Style

- Follow PEP 8 for Python code
- Use type hints where possible
- Format with `black` or `ruff`
- Lint with `pylint` or `ruff`

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Environment Variables

See `.env.example` for all required variables. Never commit `.env` files to version control.

## 🚢 Deployment

### Backend Deployment

1. **Set environment variables** on your hosting platform
2. **Run migrations**: `alembic upgrade head`
3. **Start server**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

**Recommended platforms:**
- Railway
- Render
- Fly.io
- DigitalOcean App Platform

### Frontend Deployment

**Streamlit Cloud:**
1. Push code to GitHub
2. Connect repository to [Streamlit Cloud](https://streamlit.io/cloud)
3. Set environment variables (API_BASE_URL)
4. Deploy

**Other options:**
- Docker containerization
- Traditional VPS with reverse proxy

### Database

- **Production**: Use managed PostgreSQL (Supabase, AWS RDS, etc.)
- **Backup**: Set up automated backups
- **Migrations**: Run migrations as part of deployment process

## 📝 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]

## 📞 Support

[Add support/contact information here]

## 🙏 Acknowledgments

Built with FastAPI, Streamlit, PostgreSQL, and modern Python best practices.

---

**Note**: This is a development version. For production use, ensure:
- Strong `SECRET_KEY` generation
- HTTPS enabled
- Database backups configured
- Rate limiting implemented
- Input validation enhanced
- Error logging set up
