# Setup Guide

This guide explains how to set up the Workflowz.ai FastAPI backend locally, including Python dependencies, PostgreSQL, environment variables, migrations, and OAuth2 (password flow) usage.

## Prerequisites
- Python 3.11+ recommended
- PostgreSQL 14+ recommended
- `pip` (or `pipx`/`uv` if you prefer)

## 1) Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

## 2) Install dependencies
```bash
pip install -r requirements.txt
```

## 3) Configure environment variables
Copy `.env.example` to `.env` and update values:
```bash
cp .env.example .env
```

Required variables:
- `DATABASE_URL` (async SQLAlchemy URL)
- `SECRET_KEY` (JWT signing key)
- `ALGORITHM` (JWT algorithm, default `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (e.g., 10080 for 7 days)

Example:
```
DATABASE_URL=postgresql+asyncpg://workflowz_user:password@localhost:5432/workflowz
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

## 4) PostgreSQL setup
Create a database and user (example):
```sql
CREATE USER workflowz_user WITH PASSWORD 'password';
CREATE DATABASE workflowz OWNER workflowz_user;
GRANT ALL PRIVILEGES ON DATABASE workflowz TO workflowz_user;
```

Ensure your `DATABASE_URL` matches the user, password, host, port, and database name.

## 5) Alembic migrations
Create the initial migration:
```bash
alembic revision --autogenerate -m "init"
```

Apply migrations:
```bash
alembic upgrade head
```

## 6) Run the app
```bash
uvicorn app.main:app --reload
```

Open API docs:
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## 7) OAuth2 setup (Password Flow)
This project uses **OAuth2 Password Flow** with JWT bearer tokens (FastAPI’s built-in OAuth2PasswordBearer).

### Obtain a token
`POST /api/auth/token`

Form fields:
- `username`: user email
- `password`: user password

Example with curl:
```bash
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=yourpassword"
```

Response:
```
{"access_token":"<jwt>","token_type":"bearer"}
```

### Use the token
Add the token as a Bearer token in the `Authorization` header:
```
Authorization: Bearer <jwt>
```

### Swagger UI authorization
1. Open `http://localhost:8000/docs`
2. Click **Authorize**
3. Paste the token as `Bearer <jwt>`

## 8) Creating your first superuser
The `/api/auth/register` endpoint is **superuser-only**. To bootstrap a superuser:

Option A: Insert directly into the database with a hashed password (recommended for production).

Option B: Temporarily create a superuser in the DB for local dev, then use `/api/auth/register` to add others.

If you want a management script for bootstrap, ask and I can add one.
