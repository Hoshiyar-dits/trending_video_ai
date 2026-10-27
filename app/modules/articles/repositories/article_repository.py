from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Article

class ArticleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_top(self, limit: int):
        result = await self.db.execute(select(Article).order_by(Article.score.desc()).limit(limit))
        return result.scalars().all()

    async def get(self, article_id: int):
        return await self.db.get(Article, article_id)

    async def get_by_url(self, url: str):
        result = await self.db.execute(select(Article).filter_by(url=url))
        return result.scalars().first()

    async def count(self):
        return await self.db.scalar(select(func.count()).select_from(Article))

    def add(self, article: Article):
        self.db.add(article)

    async def commit(self):
        await self.db.commit()
