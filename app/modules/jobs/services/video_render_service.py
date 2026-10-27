import asyncio
import json
import re
import subprocess
from urllib.parse import urlparse

from app.config import AUDIO_DIR, VIDEO_DIR
from app.modules.jobs.services.stock_footage_service import fetch_stock_clip
from app.video import fetch_article_images, render_animated_video, split_scenes

class VideoRenderService:
    """Plans visuals with the LLM, then renders in a worker thread (TTS + video encoding block)."""

    def __init__(self, llm):
        self.llm = llm

    async def render_video(self, script, job_id, version, article_url=""):
        scenes = split_scenes(script)
        queries = await self.plan_visuals(scenes)
        return await asyncio.to_thread(
            self._render_video, script, job_id, version, article_url, scenes, queries
        )

    def _render_video(self, script, job_id, version, article_url, scenes, queries):
        # Requires espeak-ng, ffmpeg, MoviePy 1.0.3, and Pillow.
        audio_path = AUDIO_DIR / f"job_{job_id}_v{version}.wav"
        video_path = VIDEO_DIR / f"job_{job_id}_v{version}.mp4"
        subprocess.run(
            ["espeak-ng", "-s", "160", "-w", str(audio_path), script[:4500]],
            check=True, capture_output=True
        )
        # Each scene shows a stock clip of the action it narrates; scenes without
        # a clip use the article photos (or an abstract background) with zoom/pan.
        used_ids, scene_plan = set(), []
        for index, (text, query) in enumerate(zip(scenes, queries)):
            clip_path = VIDEO_DIR / f"job_{job_id}_v{version}_scene{index}.mp4"
            scene_plan.append((text, fetch_stock_clip(query, clip_path, len(text) / 14 + 1, used_ids)))
        images = fetch_article_images(article_url)

        credits = []
        if any(clip for _, clip in scene_plan):
            credits.append("Illustrative footage: Pexels")
        if images:
            credits.append(f"Photos: {urlparse(article_url).netloc.removeprefix('www.')}")
        try:
            render_animated_video(
                script, audio_path, video_path, images, credit=" · ".join(credits),
                seed=job_id * 10 + version, scene_plan=scene_plan,
            )
        finally:
            for _, clip in scene_plan:
                if clip:
                    clip.unlink(missing_ok=True)
        return str(video_path), str(audio_path)

    async def plan_visuals(self, scenes):
        """Ask the LLM for one stock-footage search per scene describing the visible action."""
        numbered = "\n".join(f"{i + 1}. {text}" for i, text in enumerate(scenes))
        prompt = f"""
For each numbered narration line, write a short stock-video search query (2-5 words)
describing the physical action a viewer should SEE, e.g. "two men fighting",
"business people shaking hands", "crowd protesting street", "person typing laptop".
Use generic descriptions of people and places. Never use names of real people,
companies, or brands. Return ONLY a JSON array of {len(scenes)} strings, in order.
{numbered}
"""
        try:
            response = (await self.llm.ainvoke(prompt)).content
            match = re.search(r"\[.*\]", response, re.S)
            queries = [str(q).strip() for q in json.loads(match.group(0))] if match else []
        except Exception:
            queries = []
        return (queries + [""] * len(scenes))[:len(scenes)]
