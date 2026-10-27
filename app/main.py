from contextlib import asynccontextmanager
from fastapi import FastAPI

from app import models  # noqa: F401  registers all tables on Base.metadata
from app.database import Base, engine
from app.modules.articles.router import router as articles_router
from app.modules.health.router import router as health_router
from app.modules.jobs.router import router as jobs_router
from app.modules.research.router import router as research_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="AI Content Automation", version="0.1.0", lifespan=lifespan)

app.include_router(health_router)
app.include_router(research_router)
app.include_router(articles_router)
app.include_router(jobs_router)
