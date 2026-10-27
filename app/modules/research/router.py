from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.articles.repositories.article_repository import ArticleRepository
from app.modules.research.services.research_service import ResearchService

router = APIRouter(prefix="/api/research", tags=["research"])

def get_service(db: AsyncSession = Depends(get_db)) -> ResearchService:
    return ResearchService(ArticleRepository(db))

@router.post("/run")
async def run_research(service: ResearchService = Depends(get_service)):
    return await service.run_research()
