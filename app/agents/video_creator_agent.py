class VideoCreatorAgent:
    def __init__(self, script_service, render_service):
        self.script_service, self.render_service = script_service, render_service

    async def run(self, article, job, feedback=""):
        script = await self.script_service.make_script(article, feedback)
        video_path, audio_path = await self.render_service.render_video(
            script, job.id, job.retry_count + 1, article_url=article.url
        )
        job.script = script
        job.video_path = video_path
        return {"script": script, "video_path": video_path, "audio_path": audio_path}
