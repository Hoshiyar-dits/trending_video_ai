from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.articles.repositories.article_repository import ArticleRepository
from app.modules.jobs.dtos.job_out import JobOut
from app.modules.jobs.repositories.job_repository import JobRepository
from app.modules.jobs.services.job_service import JobService

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

def get_service(db: AsyncSession = Depends(get_db)) -> JobService:
    return JobService(JobRepository(db), ArticleRepository(db))

@router.post("/{job_id}/publish", response_model=JobOut)
async def publish_job(job_id: int, service: JobService = Depends(get_service)):
    return await service.publish_job(job_id)

@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: int, service: JobService = Depends(get_service)):
    return await service.get_job(job_id)
