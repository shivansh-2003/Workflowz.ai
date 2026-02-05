**Workflowz.ai** is a simple, powerful, and intuitive project management tool designed to help teams of any size organize, track, and get work done — whether you're running marketing campaigns, managing client projects, coordinating events, handling operations, or leading any kind of business initiative.

Think of it as your team's central hub where everyone knows exactly what needs to be done, who's responsible, and how things are progressing — without the confusion of endless emails, spreadsheets, or scattered notes.

### Key Benefits for Everyday Teams
- **Clear organization by company and teams** — Superuser (like the owner or admin) sets up multiple organizations (e.g., different companies or departments), each with its own isolated space so nothing gets mixed up.
- **Team structure made easy** — Within each organization, you can create teams with one clear leader (the Organization Head) and as many members as needed. Everyone has their role, name, email, and position visible.
- **Projects — where the real work lives** — Create as many projects as you need inside an organization (e.g., "New Product Launch", "Q3 Marketing Campaign", "Office Relocation"). Each project has a clear name, description, and a progress percentage that updates automatically as tasks get completed.
- **Tasks — simple and actionable** — Break projects down into individual tasks with descriptions, deadlines, priority levels (high/medium/low), and assign them directly to the right team member. The Organization Head can create, update, or remove tasks to keep everything on track.
- **Everyone can contribute** — Team members work across multiple projects within the same organization, see their assigned tasks, update progress (like marking something complete), and stay focused on what matters to them.
- **Visibility without complexity** — At a glance, leaders see overall progress, upcoming deadlines, and who's working on what — helping catch delays early and celebrate wins together.

### How It Works in Real Life
1. The superuser logs in and sets up organizations and teams.
2. Organization Heads take charge of their space — creating projects and assigning tasks to members.
3. Team members log in, see their to-do list across projects, update task status as they work, and meet deadlines.
4. Everyone stays aligned, bottlenecks disappear, and projects move forward faster — with far less back-and-forth.

Workflowz.ai is built for businesses that want the structure and clarity of professional tools (like what big teams use), but without the steep learning curve or tech-heavy feel. It's perfect for small-to-medium companies, agencies, departments, or growing teams that want to work smarter, stay organized, and deliver results — together.

Just like the most trusted tools out there, Workflowz.ai turns chaos into clarity so your team can focus on doing great work instead of chasing updates.






### Database Schema Design for Workflowz.ai Backend

Based on your description, I've designed a relational database schema using PostgreSQL syntax (adaptable to other SQL databases). This incorporates role-based access control (RBAC) implicitly through the data structure, with multi-tenancy achieved by partitioning data via `organization_name` as a key field in relevant tables. This ensures organizations are isolated from each other (e.g., queries always filter by `organization_name` to prevent cross-tenant access).

Key assumptions and decisions:
- **No dedicated organizations table**: As specified, `organization_name` is used as a string identifier (e.g., a unique key) across tables to group data. Superusers create organizations by assigning this name when creating teams and projects.
- **Multi-tenancy**: Enforced by including `organization_name` in primary/foreign keys. In the app, authentication would validate the user's `organization_name` and restrict queries accordingly.
- **Authentication**: I've added a basic `users` table to handle superusers and members. Members' details are mirrored in the `teams` table for RBAC, but authentication uses emails (assumed unique globally). Superusers are flagged separately. Use a library like JWT or OAuth for token-based auth in the backend.
- **RBAC Logic** (not in schema, but for app):
  - Superuser: Can create organizations (i.e., assign `organization_name`), teams, projects, and perform any action.
  - Organization Head: Identified by `position = 'head'` in teams. Can create/update/delete projects and tasks within their org.
  - Members: Can view/update tasks assigned to them (e.g., mark as completed).
- **Project Progress**: Stored as a percentage (0-100). In the app, calculate it dynamically based on completed tasks (e.g., via a trigger or API endpoint that counts completed tasks / total tasks * 100).
- **IDs**: Use auto-incrementing SERIAL for simplicity, but scoped within organizations via composite primary keys.
- **Tasks under Projects, Projects/Teams under Organizations**: Enforced via foreign keys.
- **Members in Multiple Projects**: Supported, as tasks reference member_id, and a member can be assigned to tasks across projects in the same org.
- **App Entry Points**: Login as superuser (checks `is_superuser = TRUE`) or member (checks `teams` table for position).
- **Additional Fields**: Added `task_completed` for progress calculation (not in your desc, but necessary). Hashed passwords for security.

#### Tables Overview

| Table Name | Purpose | Key Fields | Relationships |
|------------|---------|------------|---------------|
| users | Handles authentication for superusers and members. | user_id, email, password_hash, is_superuser | Links to teams for members via email. |
| teams | Stores team members (including heads) per organization. | organization_name, member_id, position | Foreign key to users (optional, for auth). |
| projects | Stores projects per organization. | organization_name, project_id, project_name | Created by superuser or head. |
| tasks | Stores tasks per project. | organization_name, project_id, task_id, task_assigned_to | Foreign keys to projects and teams. |

#### SQL Schema

```sql
-- Users table for authentication (superusers and members)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- Store hashed passwords (e.g., using bcrypt)
    is_superuser BOOLEAN DEFAULT FALSE,   -- TRUE for superusers
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Teams table (under organization_name, includes heads and members)
CREATE TABLE teams (
    organization_name VARCHAR(100) NOT NULL,
    member_id SERIAL NOT NULL,
    designation VARCHAR(100),
    name VARCHAR(100) NOT NULL,
    email_id VARCHAR(100) NOT NULL REFERENCES users(email),  -- Link to users for auth
    position VARCHAR(50) NOT NULL CHECK (position IN ('head', 'member')),  -- Enforce roles
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (organization_name, member_id),
    UNIQUE (organization_name, email_id)  -- Prevent duplicate emails per org
);

-- Projects table (under organization_name)
CREATE TABLE projects (
    organization_name VARCHAR(100) NOT NULL,
    project_id SERIAL NOT NULL,
    project_name VARCHAR(100) NOT NULL,
    project_description TEXT,
    project_progress INTEGER DEFAULT 0 CHECK (project_progress BETWEEN 0 AND 100),  -- % based on tasks
    created_by VARCHAR(100) NOT NULL,  -- Email of superuser or head who created it
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (organization_name, project_id),
    UNIQUE (organization_name, project_name)  -- Prevent duplicate project names per org
);

-- Tasks table (under project, via organization_name and project_id)
CREATE TABLE tasks (
    organization_name VARCHAR(100) NOT NULL,
    project_id INTEGER NOT NULL,
    task_id SERIAL NOT NULL,
    task_description TEXT NOT NULL,
    task_deadline DATE,
    task_assigned_to INTEGER NOT NULL,  -- References member_id in teams
    task_importance VARCHAR(50) CHECK (task_importance IN ('high', 'medium', 'low')),  -- Assuming levels
    task_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (organization_name, project_id, task_id),
    FOREIGN KEY (organization_name, project_id) REFERENCES projects(organization_name, project_id) ON DELETE CASCADE,
    FOREIGN KEY (organization_name, task_assigned_to) REFERENCES teams(organization_name, member_id) ON DELETE RESTRICT
);
```

#### Example Data Flow and RBAC Enforcement
- **Superuser Creates Organization and Team**:
  - Insert into `users` (if new superuser).
  - Create team: `INSERT INTO teams (organization_name, member_id, ..., position) VALUES ('OrgA', ..., 'head');`
  - The head's email must exist in `users`.

- **Creating Project**:
  - Superuser or head: `INSERT INTO projects (organization_name, project_id, ...) VALUES ('OrgA', ...);`
  - App checks if user is superuser or head in `teams` for that org.

- **Assigning Tasks**:
  - Head only: `INSERT INTO tasks (organization_name, project_id, task_assigned_to, ...) VALUES ('OrgA', 1, 2, ...);`
  - App validates position='head'.

- **Updating Project Progress**:
  - Use a SQL function or app logic: `UPDATE projects SET project_progress = (SELECT (COUNT(*) FILTER (WHERE task_completed) * 100 / COUNT(*)) FROM tasks WHERE organization_name = 'OrgA' AND project_id = 1) WHERE organization_name = 'OrgA' AND project_id = 1;`

- **Multi-Tenancy Queries**:
  - Always include `WHERE organization_name = '<user_org>'` in API queries, based on authenticated user's org from `teams`.

#### Backend Implementation Suggestions
- **Framework**: Use Node.js with Express, Python with Flask/Django, or Java with Spring for the backend API.
- **API Endpoints** (high-level):
  - `/login`: POST {email, password} → Returns JWT token with role (superuser/head/member) and org_name.
  - `/organizations`: POST (superuser only) → Creates a new org by adding a head to teams.
  - `/teams`: GET/POST (superuser or head) → Manage teams in org.
  - `/projects`: GET/POST/PUT/DELETE (superuser or head).
  - `/tasks`: GET/POST/PUT/DELETE (head for create/update/delete; members for their assigned tasks).
- **Security**: Use middleware to check JWT role and org_name. Hash passwords. Validate inputs to prevent SQL injection.
- **Progress Calculation**: Trigger on task update/completion to recalculate project_progress.

If you need code for a specific framework (e.g., Flask app skeleton), API documentation, or ER diagram (I can describe it textually if needed), let me know! Also, if this schema misses anything, provide more details.

Here is a **technical implementation overview** for **Workflowz.ai** — a multi-tenant, role-based project/task management backend built with modern Python tools.

### Chosen Tech Stack
- **Framework** — **FastAPI** (async, automatic OpenAPI docs, excellent dependency injection)
- **ORM & Database Access** — **SQLAlchemy 2.x** (with async support via `asyncio`)
- **Data Validation & Serialization** — **Pydantic v2** (native in FastAPI)
- **Authentication** — **OAuth2 Password Flow + JWT Bearer** (using `PyJWT` or `python-jose[cryptography]`)
- **Password Hashing** — **passlib** with **bcrypt**
- **Database** — **PostgreSQL** (production-ready, good JSON support if needed later)
- **Dependencies & Security** — FastAPI `Depends`, custom security dependencies
- **Project Structure** — Clean, modular, domain-driven layout

### High-Level Project Structure
```
workflowz-ai/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry
│   ├── core/
│   │   ├── config.py            # Settings (pydantic-settings or dotenv)
│   │   ├── security.py          # JWT create/verify, password hash/verify
│   │   └── exceptions.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── session.py           # get_db dependency (async session)
│   │   └── models/              # All SQLAlchemy models
│   ├── schemas/                 # Pydantic models (in/out)
│   │   ├── auth.py
│   │   ├── organization.py
│   │   ├── team.py
│   │   ├── project.py
│   │   └── task.py
│   ├── dependencies/
│   │   ├── auth.py              # get_current_user, get_current_head, etc.
│   │   └── tenancy.py           # get_organization_from_user
│   ├── routers/
│   │   ├── auth.py
│   │   ├── superuser.py         # Org & team creation
│   │   ├── teams.py
│   │   ├── projects.py
│   │   └── tasks.py
│   └── crud/                    # CRUD operations (optional — can be in routers)
│       ├── user.py
│       ├── team.py
│       ├── project.py
│       └── task.py
├── .env
├── requirements.txt
└── alembic/                     # Database migrations
```

### 1. Database Models (SQLAlchemy)
Use the schema from earlier conversation — slightly adapted for SQLAlchemy style.

```python
# app/database/models/__init__.py
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Date, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_superuser = Column(Boolean, default=False)

class TeamMember(Base):
    __tablename__ = "teams"
    organization_name = Column(String(100), primary_key=True)
    member_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    designation = Column(String(100))
    position = Column(String(50), nullable=False)  # 'head' or 'member'
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")

class Project(Base):
    __tablename__ = "projects"
    organization_name = Column(String(100), primary_key=True)
    project_id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String(100), nullable=False)
    project_description = Column(Text)
    project_progress = Column(Integer, default=0)
    created_by = Column(String(100), nullable=False)  # email

class Task(Base):
    __tablename__ = "tasks"
    organization_name = Column(String(100), primary_key=True)
    project_id = Column(Integer, primary_key=True)
    task_id = Column(Integer, primary_key=True, autoincrement=True)
    task_description = Column(Text, nullable=False)
    task_deadline = Column(Date)
    task_assigned_to = Column(Integer, nullable=False)           # team member_id
    task_importance = Column(String(50))
    task_completed = Column(Boolean, default=False)
```

**Multi-tenancy note** — All queries must filter by `organization_name`. This is enforced via dependencies.

### 2. Authentication & JWT (core/security.py)

```python
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from pydantic import BaseModel

SECRET_KEY = "your-very-long-random-secret"  # Use env var in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7   # 1 week

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TokenData(BaseModel):
    email: str | None = None
    is_superuser: bool = False

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### 3. Authentication Dependency (dependencies/auth.py)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from .security import TokenData, SECRET_KEY, ALGORITHM
from ..database.session import get_db
from ..database.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = await db.get(User, email=token_data.email)  # or query
    if user is None:
        raise credentials_exception
    return user
```

**Role-based dependencies** (examples):

```python
async def get_current_superuser(current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Superuser access required")
    return current_user

async def get_current_org_head(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Query TeamMember where email matches and position == 'head'
    # Raise 403 if not head in that organization
    ...
```

### 4. Routers & Endpoints (Example: projects.py)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..dependencies.auth import get_current_user, get_current_superuser, get_current_org_head
from ..schemas.project import ProjectCreate, ProjectOut
from ..crud.project import create_project, get_projects

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ProjectOut)
async def create_new_project(
    project: ProjectCreate,
    current_user = Depends(get_current_org_head),  # or superuser
    db: AsyncSession = Depends(get_db)
):
    # Automatically use current_user.organization_name
    return await create_project(db, project, organization_name=current_user.organization_name)

@router.get("/")
async def list_projects(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_projects(db, organization_name=current_user.organization_name)
```

### 5. Multi-Tenancy Enforcement Pattern
Every protected router/endpoint uses a dependency that:

1. Gets current user → extracts organization_name (from TeamMember table)
2. Injects `organization_name` into CRUD functions
3. All queries include `.filter(Team.organization_name == org_name)`

**Example CRUD helper**:

```python
async def get_projects(db: AsyncSession, organization_name: str):
    result = await db.execute(
        select(Project).where(Project.organization_name == organization_name)
    )
    return result.scalars().all()
```

### 6. Recommended Next Steps
1. Set up **Alembic** for migrations
2. Add **`.env`** with:
   ```
   DATABASE_URL=postgresql+asyncpg://user:pass@localhost/workflowz
   SECRET_KEY=supersecret...
   ```
3. Implement **login endpoint** (`/auth/token`) → returns JWT
4. Add **task completion** → update `project_progress` (via trigger or app logic)
5. Use **FastAPI Users** or **fastapi-users** library if you want to speed up auth boilerplate
6. Add **rate limiting**, **CORS**, **logging**

This structure gives you:
- Secure JWT auth
- Strict multi-tenancy
- Role checks via dependencies (superuser, org head, member)
- Clean separation of concerns

Let me know which part you'd like to see in full code (e.g. full auth router, project CRUD, or alembic setup), or if you want to change any decision (e.g. add refresh tokens, use fastapi-users, etc.)!



Here’s a clear and focused addition to the **Workflowz.ai** project description and technical implementation, specifically addressing:

1. Weighted progress logic (based only on tasks)
2. Superuser capabilities regarding organizations (create, update name, assign/update head)

### Additional Project Description (Non-Technical – User-Facing)

**Workflowz.ai – Enhanced Features**

- **Smart Progress Tracking**  
  Every project shows a clear progress percentage that updates automatically. The progress is calculated **only from the tasks** inside that project — no manual input needed.  
  Each task can have different importance levels (High, Medium, Low), and the system gives **more weight** to important tasks when calculating overall progress. This way, completing a critical task moves the project forward more noticeably than finishing a minor one.

- **Superuser Controls – Full Organization Management**  
  The superuser (system admin or owner) has powerful tools to manage organizations:  
  - Create new organizations with a unique name  
  - Change the name of any organization at any time  
  - Assign or change the **Organization Head** (the leader of the team)  
  - Replace the head whenever needed (e.g., when someone leaves or role changes)  

  This gives the superuser complete control over the structure of the company or departments, while each organization remains fully isolated from the others.

These features make Workflowz.ai even more flexible for growing teams and businesses that need both clear visibility into work progress and strong administrative control.

---

### Technical Implementation – Weighted Task Progress Logic

#### Goal
Calculate `project_progress` (0–100%) based **only on tasks**, with **weighted contribution** depending on `task_importance`.

#### Assumptions for Weighting
| Importance  | Weight |
|-------------|--------|
| high        | 3      |
| medium      | 2      |
| low         | 1      |

- A completed **high** importance task contributes 3× more toward progress than a completed **low** one.
- Progress = (sum of weights of completed tasks) / (sum of weights of all tasks) × 100

#### Database Change (if not already present)
Make sure `task_importance` uses consistent values:

```sql
ALTER TABLE tasks
ALTER COLUMN task_importance TYPE VARCHAR(50)
CHECK (task_importance IN ('high', 'medium', 'low', NULL));
```

#### Option 1: Calculate Progress in Application Layer (Recommended for FastAPI)

**Pydantic schema** (schemas/task.py or project.py)

```python
from pydantic import BaseModel

class ProjectProgressUpdate(BaseModel):
    project_progress: int
```

**CRUD function** (crud/project.py)

```python
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.models import Task, Project

async def recalculate_project_progress(
    db: AsyncSession,
    organization_name: str,
    project_id: int
) -> int:
    # Get all tasks for this project
    stmt = select(Task).where(
        Task.organization_name == organization_name,
        Task.project_id == project_id
    )
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    if not tasks:
        return 0

    total_weight = 0
    completed_weight = 0

    weight_map = {"high": 3, "medium": 2, "low": 1, None: 1}

    for task in tasks:
        weight = weight_map.get(task.task_importance, 1)
        total_weight += weight
        if task.task_completed:
            completed_weight += weight

    if total_weight == 0:
        progress = 0
    else:
        progress = int((completed_weight / total_weight) * 100)

    # Update project
    project_stmt = select(Project).where(
        Project.organization_name == organization_name,
        Project.project_id == project_id
    )
    project = (await db.execute(project_stmt)).scalar_one_or_none()

    if project:
        project.project_progress = progress
        await db.commit()
        await db.refresh(project)

    return progress
```

**When to call it**
- After creating a task → `await recalculate_project_progress(...)`
- After updating `task_completed` (PATCH task endpoint)
- After deleting a task

**Task update example** (in router)

```python
@router.patch("/{task_id}/complete")
async def mark_task_complete(
    task_id: int,
    complete: bool,
    current_head = Depends(get_current_org_head),
    db: AsyncSession = Depends(get_db)
):
    # ... find task, update task_completed = complete
    await db.commit()
    await recalculate_project_progress(db, current_head.organization_name, project_id)
    return {"status": "updated", "progress_updated": True}
```

#### Option 2: Use PostgreSQL Trigger (Fully Automatic)

```sql
CREATE OR REPLACE FUNCTION update_project_progress()
RETURNS TRIGGER AS $$
BEGIN
    WITH weights AS (
        SELECT 
            SUM(
                CASE 
                    WHEN task_importance = 'high' THEN 3
                    WHEN task_importance = 'medium' THEN 2
                    WHEN task_importance = 'low' THEN 1
                    ELSE 1
                END
            ) AS total_weight,
            SUM(
                CASE 
                    WHEN task_completed THEN
                        CASE 
                            WHEN task_importance = 'high' THEN 3
                            WHEN task_importance = 'medium' THEN 2
                            WHEN task_importance = 'low' THEN 1
                            ELSE 1
                        END
                    ELSE 0
                END
            ) AS completed_weight
        FROM tasks
        WHERE organization_name = NEW.organization_name
          AND project_id = NEW.project_id
    )
    UPDATE projects
    SET project_progress = COALESCE(
        CASE 
            WHEN (SELECT total_weight FROM weights) = 0 THEN 0
            ELSE ((SELECT completed_weight FROM weights) * 100 / (SELECT total_weight FROM weights))::integer
        END, 0
    )
    WHERE organization_name = NEW.organization_name
      AND project_id = NEW.project_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER task_progress_trigger
AFTER INSERT OR UPDATE OF task_completed, task_importance OR DELETE
ON tasks
FOR EACH ROW
EXECUTE FUNCTION update_project_progress();
```

This way, progress is **always correct** even if someone updates the database directly.

---

### Superuser – Organization Management

#### New Endpoints (routers/superuser.py)

```python
router = APIRouter(prefix="/superuser/organizations", tags=["superuser-organizations"])

@router.post("/")
async def create_organization(
    org_name: str,
    head_email: str,
    current_superuser = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    # 1. Check head_email exists in users
    # 2. Insert into teams: organization_name, position='head', email_id=head_email, user_id=...
    # 3. Can optionally create default project or just leave empty
    ...

@router.patch("/{organization_name}")
async def update_organization_name(
    organization_name: str,
    new_name: str,
    current_superuser = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    # Update ALL rows in teams, projects, tasks where organization_name = old → new
    # Be careful — this is a bulk update
    await db.execute(
        update(TeamMember).where(TeamMember.organization_name == organization_name)
        .values(organization_name=new_name)
    )
    # Same for Project and Task tables
    await db.commit()
    ...

@router.patch("/{organization_name}/head")
async def change_organization_head(
    organization_name: str,
    new_head_email: str,
    current_superuser = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    # 1. Validate new_head_email exists
    # 2. Set old head → position='member'
    # 3. Set new head → position='head'
    ...
```

This gives superuser full lifecycle control over organizations.

Let me know if you want the full code for any of these endpoints, the trigger script, or adjustments to the weighting logic!