from sqlalchemy.ext.asyncio import AsyncSession

from app.models import VideoReview

class ReviewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, job_id: int, approved: bool, score: float, issues: str, feedback: str):
        review = VideoReview(job_id=job_id, approved=approved, score=score, issues=issues, feedback=feedback)
        self.db.add(review)
        await self.db.commit()
        return review
