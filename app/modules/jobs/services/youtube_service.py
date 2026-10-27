import asyncio
from pathlib import Path

from app.config import YOUTUBE_PUBLIC_PUBLISHING_ENABLED, YOUTUBE_PRIVACY_STATUS
from app.modules.jobs.services.youtube_auth import load_credentials

class YouTubeService:
    async def publish_youtube(self, video_path, title, description):
        return await asyncio.to_thread(self._publish_youtube, video_path, title, description)

    def _publish_youtube(self, video_path, title, description):
        if not YOUTUBE_PUBLIC_PUBLISHING_ENABLED:
            return None, "Public publishing is disabled in configuration."
        if not Path(video_path or "").exists():
            return None, f"Video file not found: {video_path}"
        creds = load_credentials()
        if not creds:
            return None, "YouTube is not authorised yet. Run: python -m app.modules.jobs.services.youtube_auth"

        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        # Vertical videos under 3 minutes with #Shorts are listed as YouTube Shorts.
        suffix = " #Shorts"
        youtube = build("youtube", "v3", credentials=creds)
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title[:100 - len(suffix)] + suffix,
                    "description": f"{description}\n\n#Shorts #news"[:5000],
                    "categoryId": "25",
                },
                "status": {"privacyStatus": YOUTUBE_PRIVACY_STATUS, "selfDeclaredMadeForKids": False},
            },
            media_body=MediaFileUpload(video_path, mimetype="video/mp4", resumable=True),
        )
        response = request.execute()
        video_id = response["id"]
        return video_id, f"https://www.youtube.com/watch?v={video_id}"
