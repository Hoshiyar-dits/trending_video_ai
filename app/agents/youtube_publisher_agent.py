class YouTubePublisherAgent:
    def __init__(self, youtube_service):
        self.youtube_service = youtube_service

    async def run(self, article, job):
        video_id, url = await self.youtube_service.publish_youtube(
            job.video_path,
            title=article.title,
            description=f"{article.summary}\n\nSource: {article.url}",
        )
        if not video_id:
            return {"published": False, "message": url}
        job.youtube_video_id = video_id
        job.youtube_url = url
        return {"published": True, "video_id": video_id, "url": url}
