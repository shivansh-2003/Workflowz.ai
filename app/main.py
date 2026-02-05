from fastapi import FastAPI

from app.core.config import settings
from app.routers import auth, projects, superuser, tasks, teams

app = FastAPI(title=settings.APP_NAME)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(superuser.router, prefix=settings.API_V1_PREFIX)
app.include_router(teams.router, prefix=settings.API_V1_PREFIX)
app.include_router(projects.router, prefix=settings.API_V1_PREFIX)
app.include_router(tasks.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}
