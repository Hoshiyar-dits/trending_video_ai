from sqlalchemy.ext.asyncio import AsyncSession

from app.models import VideoJob

class JobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, job_id: int):
        return await self.db.get(VideoJob, job_id)

    async def create(self, article_id: int, status: str = "queued"):
        job = VideoJob(article_id=article_id, status=status)
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def save(self, job: VideoJob):
        """Commit pending changes to `job` (and anything else in the session)."""
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def rollback(self):
        await self.db.rollback()
