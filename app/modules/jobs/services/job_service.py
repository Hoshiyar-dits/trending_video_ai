from fastapi import HTTPException

from app.agents import YouTubePublisherAgent
from app.modules.articles.repositories.article_repository import ArticleRepository
from app.modules.jobs.repositories.job_repository import JobRepository
from app.modules.jobs.services.youtube_service import YouTubeService

class JobService:
    def __init__(self, jobs: JobRepository, articles: ArticleRepository):
        self.jobs, self.articles = jobs, articles

    async def get_job(self, job_id: int):
        job = await self.jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job

    async def publish_job(self, job_id: int):
        job = await self.get_job(job_id)
        if job.youtube_video_id:
            raise HTTPException(status_code=409, detail=f"Already published: {job.youtube_url}")
        if not job.status.startswith("approved"):
            raise HTTPException(status_code=409, detail=f"Job status is '{job.status}'; only approved videos can be published")
        article = await self.articles.get(job.article_id)
        try:
            result = await YouTubePublisherAgent(YouTubeService()).run(article, job)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"YouTube upload failed: {exc}")
        if not result["published"]:
            raise HTTPException(status_code=400, detail=result["message"])
        job.status = "published"
        return await self.jobs.save(job)
