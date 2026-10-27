from fastapi import HTTPException

from app.llm import build_llm
from app.modules.articles.repositories.article_repository import ArticleRepository
from app.modules.jobs.repositories.job_repository import JobRepository
from app.modules.jobs.repositories.review_repository import ReviewRepository
from app.workflow import ContentWorkflow

class ArticleService:
    def __init__(self, articles: ArticleRepository, jobs: JobRepository, reviews: ReviewRepository):
        self.articles, self.jobs, self.reviews = articles, jobs, reviews

    async def list_articles(self, limit: int):
        return await self.articles.list_top(min(max(limit, 1), 100))

    async def get_article(self, article_id: int):
        article = await self.articles.get(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return article

    async def process_article(self, article_id: int, publish: bool):
        article = await self.get_article(article_id)
        job = await self.jobs.create(article.id)
        try:
            workflow = ContentWorkflow(build_llm())
            await workflow.run(article, job, self.jobs, self.reviews, publish_requested=publish)
            return job
        except Exception as exc:
            await self.jobs.rollback()
            job.status = "failed"
            job.error = str(exc)
            await self.jobs.save(job)
            raise HTTPException(status_code=500, detail=f"Workflow failed: {exc}")
