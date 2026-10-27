from app.models import Article

class TrendResearcherAgent:
    def __init__(self, news_feed):
        self.news_feed = news_feed

    async def run(self, article_repo):
        added = 0
        for item in await self.news_feed.fetch_articles():
            existing = await article_repo.get_by_url(item["url"])
            if existing:
                continue
            score = await self.news_feed.rank_article(item)
            article_repo.add(Article(**item, score=score))
            added += 1
        await article_repo.commit()
        return {"added": added, "total": await article_repo.count()}
