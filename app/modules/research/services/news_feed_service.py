import asyncio
import json
import re
from urllib.parse import urlparse

import feedparser

from app.config import RSS_FEEDS

class NewsFeedService:
    def __init__(self, llm):
        self.llm = llm

    async def fetch_articles(self):
        return await asyncio.to_thread(self._fetch_articles)

    def _fetch_articles(self):
        results = []
        for feed_url in RSS_FEEDS:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:30]:
                url = getattr(entry, "link", "")
                title = getattr(entry, "title", "").strip()
                if not url or not title or len(url) > 768:
                    continue
                summary = re.sub("<[^>]+>", " ", getattr(entry, "summary", "")).strip()
                results.append({
                    "title": title[:500],
                    "url": url,
                    "source": urlparse(feed_url).netloc,
                    "summary": summary[:5000],
                    "content": summary[:12000],
                    "published_at": str(getattr(entry, "published", "")),
                })
        return results

    async def rank_article(self, article):
        prompt = (
            "Rate this news item for potential interest in a short educational video. "
            "Return only JSON like {\"score\": 0-100, \"reason\": \"...\"}. "
            "Do not claim to have live trend statistics.\n"
            f"Title: {article['title']}\nSummary: {article['summary']}"
        )
        try:
            result = (await self.llm.ainvoke(prompt)).content
            match = re.search(r"\{.*\}", result, re.S)
            data = json.loads(match.group(0)) if match else {}
            return float(max(0, min(100, float(data.get("score", 50)))))
        except Exception:
            return 50.0
