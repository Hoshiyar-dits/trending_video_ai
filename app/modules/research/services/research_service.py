from fastapi import HTTPException

from app.agents import TrendResearcherAgent
from app.llm import build_llm
from app.modules.articles.repositories.article_repository import ArticleRepository
from app.modules.research.services.news_feed_service import NewsFeedService

class ResearchService:
    def __init__(self, articles: ArticleRepository):
        self.articles = articles

    async def run_research(self):
        try:
            return await TrendResearcherAgent(NewsFeedService(build_llm())).run(self.articles)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Research failed: {exc}")
