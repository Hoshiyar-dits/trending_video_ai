import asyncio
from pathlib import Path

class VideoCheckService:
    async def technical_video_check(self, video_path):
        path = Path(video_path)
        if not path.exists() or path.stat().st_size < 1000:
            return False, "Rendered video file is missing or too small."
        process = await asyncio.create_subprocess_exec(
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await process.communicate()
        if process.returncode != 0 or not stdout.strip():
            return False, "FFprobe could not validate the video."
        return True, "Video file exists and FFprobe can read its duration."
