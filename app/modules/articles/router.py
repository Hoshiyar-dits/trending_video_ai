from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.articles.dtos.article_out import ArticleOut
from app.modules.articles.dtos.process_request import ProcessRequest
from app.modules.articles.repositories.article_repository import ArticleRepository
from app.modules.articles.services.article_service import ArticleService
from app.modules.jobs.dtos.job_out import JobOut
from app.modules.jobs.repositories.job_repository import JobRepository
from app.modules.jobs.repositories.review_repository import ReviewRepository

router = APIRouter(prefix="/api/articles", tags=["articles"])

def get_service(db: AsyncSession = Depends(get_db)) -> ArticleService:
    return ArticleService(ArticleRepository(db), JobRepository(db), ReviewRepository(db))

@router.get("", response_model=list[ArticleOut])
async def list_articles(limit: int = 20, service: ArticleService = Depends(get_service)):
    return await service.list_articles(limit)

@router.get("/{article_id}", response_model=ArticleOut)
async def get_article(article_id: int, service: ArticleService = Depends(get_service)):
    return await service.get_article(article_id)

@router.post("/{article_id}/process", response_model=JobOut)
async def process_article(article_id: int, body: ProcessRequest, service: ArticleService = Depends(get_service)):
    return await service.process_article(article_id, body.publish)
