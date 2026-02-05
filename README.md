# Workflowz.ai Backend

FastAPI backend for Workflowz.ai with multi-tenancy, RBAC, and weighted task-based project progress.

## Setup
1. Create a virtual environment and install dependencies:
   - `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and update values.
3. Initialize and apply migrations:
   - `alembic upgrade head`
4. Run the app:
   - `uvicorn app.main:app --reload`

## API
The API is served under `/api`. OpenAPI docs are available at `/docs`.
