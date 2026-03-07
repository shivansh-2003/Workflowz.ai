# Workflowz.ai — Claude Code Guide

## Project Overview

AI-powered project management platform with a 7-stage human-in-the-loop agentic pipeline for task decomposition. Multi-tenant SaaS with RBAC, async FastAPI backend, Streamlit frontend, and LangGraph orchestration.

## Architecture

```
workflowz_ai/
├── app/                        # FastAPI backend
│   ├── agents/                 # LangGraph agentic pipeline
│   ├── core/                   # Config, security, exceptions
│   ├── crud/                   # Data access layer
│   ├── database/               # SQLAlchemy models & session
│   ├── dependencies/           # FastAPI DI (auth, tenancy)
│   ├── routers/                # API route handlers
│   ├── schemas/                # Pydantic request/response models
│   └── main.py                 # FastAPI entry point
├── workflowz-ui/               # Streamlit frontend
│   ├── app.py                  # Entry point (login/signup)
│   ├── pages/                  # Multi-page Streamlit app
│   ├── components/             # Reusable UI components
│   ├── services/               # API client layer
│   └── utils/                  # Helpers (config, formatters, jwt, state)
├── alembic/                    # DB migrations
├── requirements.txt            # Backend dependencies
└── .env.example                # Environment variable template
```

## Running the Project

### Backend

```bash
# Activate venv, install deps
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env  # Set DATABASE_URL, SECRET_KEY, OLLAMA_* vars

# Run migrations
alembic upgrade head

# Start Ollama (required for AI features)
ollama serve
ollama pull gpt-oss:20b  # or whichever model is configured

# Start API server
uvicorn app.main:app --reload
# API: http://localhost:8000  |  Docs: http://localhost:8000/docs
```

### Frontend

```bash
cd workflowz-ui
pip install -r requirements.txt
streamlit run app.py
# UI: http://localhost:8501
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Uvicorn |
| Database | PostgreSQL (async), SQLAlchemy 2.x, Alembic |
| Auth | JWT (python-jose), bcrypt (passlib) |
| AI/Agents | LangChain, LangGraph, LangChain-Ollama |
| Observability | Langfuse (optional) |
| Frontend | Streamlit, httpx |
| Validation | Pydantic v2, pydantic-settings |

## AI Agentic Pipeline

7-stage LangGraph state machine in `app/agents/`:

1. **Input Ingestion** (`input_ingestion_agent.py`) — normalize project description
2. **Architecture Context** (`architecture_context_agent.py`) — classify system type
3. **Clarification** (`clarification_agent.py`) — generate risk questions → **WAIT_FOR_USER** (HITL pause)
4. **Team Capability Model** (in orchestrator) — snapshot team skills from DB
5. **Task Decomposition** (`task_decomposition_agent.py`) — generate team-aware tasks
6. **Role-Task Matching** (`role_task_matching_agent.py`) — validate feasibility, balance workload
7. **Validation & Risk** (`validation_risk_agent.py`) — independent audit → **HUMAN_APPROVAL** pause → persist

State is persisted in the `ai_workflow_state` DB table (JSONB), making the pipeline crash-safe and resumable.

Key files:
- `app/agents/orchestrator.py` — state machine, workflow composition
- `app/agents/llm_config.py` — LLM provider configuration
- `app/agents/prompts.py` — all LLM prompts
- `app/agents/backend_client.py` — agent→DB data access
- `app/agents/langfuse_integration.py` — observability hooks

## Database Models

Defined in `app/database/models/`:
- `User` — accounts, superuser flag
- `Team` — org members with roles (`head` / `member`) and designations
- `Project` — projects with auto-calculated progress
- `Task` — assignments, deadlines, priorities, completion status
- `AIWorkflowState` — agent pipeline state (JSONB)

Multi-tenancy is enforced via organization scoping in `app/dependencies/`.

## API Endpoints

| Router | Prefix | Notes |
|--------|--------|-------|
| `auth.py` | `/api/auth` | signup, token (OAuth2 password flow), register |
| `superuser.py` | `/api/superuser` | org creation, admin operations |
| `teams.py` | `/api/teams` | team CRUD |
| `projects.py` | `/api/projects` | project CRUD |
| `tasks.py` | `/api/tasks` | task CRUD, filtering |
| `ai.py` | `/api/projects/{id}/ai` | start pipeline, submit clarifications, approve plan |

## Environment Variables

Key vars from `.env.example`:
- `DATABASE_URL` — async PostgreSQL connection string (`postgresql+asyncpg://...`)
- `SECRET_KEY` — JWT signing key
- `ALGORITHM` — JWT algorithm (default `HS256`)
- `OLLAMA_BASE_URL` — Ollama server URL (default `http://localhost:11434`)
- `OLLAMA_MODEL` — model name (e.g. `gpt-oss:20b`)
- `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` — optional observability

## Conventions

- **Async throughout**: all DB operations use `async/await` with `asyncpg`
- **Type hints everywhere**: Pydantic models for all API boundaries
- **CRUD layer**: DB access always goes through `app/crud/`, not directly in routers
- **Schemas**: separate `Create`, `Update`, `Response` Pydantic models per entity
- **Dependency injection**: auth and tenancy enforced via FastAPI `Depends()` in `app/dependencies/`
- **Multi-tenant scoping**: queries always filter by organization — never leak cross-tenant data
- **Agent contracts**: each agent receives and returns a typed envelope; see `agent_deatil.md`

## No Tests Yet

There is currently no test suite. When adding tests:
- Backend: use `pytest` + `httpx.AsyncClient` with FastAPI's test client
- Mock LLM calls when testing agent logic
- Use a separate test database (configure via env)

## Key Documentation

- `README.md` — features, setup, API overview
- `setup.md` — detailed PostgreSQL + environment setup
- `agent_deatil.md` — agentic design philosophy, agent APIs, state machine diagram
- `details.md` — extended platform documentation
- `app/routers/README.md`, `app/database/README.md`, etc. — component-level docs
