
"""Download free stock clips from Pexels that match what the narration describes."""
import subprocess
import tempfile
from pathlib import Path

import requests

from app.config import PEXELS_API_KEY

SEARCH_URL = "https://api.pexels.com/videos/search"


def _search(query, orientation):
    params = {"query": query, "per_page": 10, "size": "medium"}
    if orientation:
        params["orientation"] = orientation
    response = requests.get(SEARCH_URL, headers={"Authorization": PEXELS_API_KEY}, params=params, timeout=15)
    response.raise_for_status()
    return response.json().get("videos", [])


def _best_file(video):
    files = [f for f in video.get("video_files", [])
             if f.get("file_type") == "video/mp4" and (f.get("height") or 0) >= 720]
    # Smallest file that is still sharp enough for a 720x1280 frame.
    return min(files, key=lambda f: f["height"] * f["width"], default=None)


def fetch_stock_clip(query, dest, min_seconds, used_ids, width=720, height=1280):
    """Download a clip for `query`, cropped to the vertical frame. Returns the path or None."""
    if not PEXELS_API_KEY or not query:
        return None
    try:
        videos = _search(query, "portrait") or _search(query, None)
    except requests.RequestException:
        return None
    # Prefer clips long enough to cover the scene without looping.
    videos.sort(key=lambda v: v.get("duration", 0) < min_seconds)
    for video in videos:
        if video["id"] in used_ids:
            continue
        file = _best_file(video)
        if not file:
            continue
        with tempfile.NamedTemporaryFile(suffix=".mp4") as raw:
            try:
                with requests.get(file["link"], stream=True, timeout=30) as response:
                    response.raise_for_status()
                    for block in response.iter_content(1 << 20):
                        raw.write(block)
                raw.flush()
                subprocess.run(
                    ["ffmpeg", "-y", "-v", "error", "-i", raw.name, "-an", "-t", str(min_seconds + 2),
                     "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,"
                            f"crop={width}:{height},fps=24",
                     "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", str(dest)],
                    check=True, capture_output=True,
                )
            except (requests.RequestException, subprocess.CalledProcessError):
                continue
        used_ids.add(video["id"])
        return Path(dest)
    return None
