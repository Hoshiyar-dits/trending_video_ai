import math
import os
import random
from pathlib import Path

import numpy as np
from moviepy.editor import AudioFileClip, VideoClip

from app.video.constants import H, FPS, SCENE_SECONDS, FADE
from app.video.captions import caption_chunks, chunk_weight, caption_timings, render_caption
from app.video.images import fallback_background, cover_image
from app.video.image_scene import ImageScene
from app.video.video_scene import VideoScene
from app.video.utils import load_font, smooth

def _bottom_shade(height=520, strength=0.65):
    alpha = np.linspace(0, strength, height, dtype=np.float32) ** 1.5
    return alpha[:, None, None]

def render_animated_video(script, audio_path, video_path, images, credit="", seed=0, scene_plan=None):
    """scene_plan: optional list of (scene_text, clip_path_or_None) from split_scenes();
    scenes then change with the narration and show the clip, or a photo when it is None."""
    rng = random.Random(seed)
    audio = AudioFileClip(str(audio_path))
    duration = audio.duration

    if not images:
        images = [fallback_background(seed + i) for i in range(2)]
    covers = [cover_image(image) for image in images]
    if scene_plan:
        # Same weights as the captions, so a scene cut lands where its sentence starts.
        weights = [sum(chunk_weight(c) for c in caption_chunks(text)) or 1 for text, _ in scene_plan]
        clips = [clip for _, clip in scene_plan]
    else:
        n = max(len(covers), math.ceil(duration / SCENE_SECONDS))
        weights, clips = [1] * n, [None] * n
    n_scenes = len(weights)
    bounds = [duration * sum(weights[:i]) / sum(weights) for i in range(n_scenes + 1)]

    scenes, last_motion, photo_index = [], None, 0
    for clip in clips:
        if clip:
            scenes.append(VideoScene(clip))
            continue
        motion = rng.choice([m for m in ImageScene.MOTIONS if m != last_motion])
        scenes.append(ImageScene(covers[photo_index % len(covers)], motion, rng))
        photo_index += 1
        last_motion = motion

    font = load_font(46)
    captions = [(start, end, *render_caption(text, font))
                for start, end, text in caption_timings(caption_chunks(script), duration)]
    shade = _bottom_shade()
    credit_layer = render_caption(credit, load_font(20)) if credit else None

    def scene_frame(i, t):
        start = bounds[i] - FADE
        return scenes[i].frame((t - start) / (bounds[i + 1] - start), max(t - start, 0.0))

    def make_frame(t):
        i = next((k for k in range(n_scenes) if t < bounds[k + 1]), n_scenes - 1)
        frame = scene_frame(i, t)
        fade_start = bounds[i + 1] - FADE
        if i + 1 < n_scenes and t > fade_start:
            a = smooth((t - fade_start) / FADE)
            frame = frame * (1 - a) + scene_frame(i + 1, t) * a

        frame[-shade.shape[0]:] *= 1 - shade
        for start, end, rgb, alpha in captions:
            if start <= t < end:
                # Quick fade-in so captions don't pop.
                alpha = alpha * min(1.0, (t - start) / 0.15)
                y = H - 300 - rgb.shape[0] // 2
                region = frame[y:y + rgb.shape[0]]
                region[:] = region * (1 - alpha) + rgb * alpha
                break
        if credit_layer:
            rgb, alpha = credit_layer
            region = frame[30:30 + rgb.shape[0]]
            region[:] = region * (1 - alpha * 0.8) + rgb * alpha * 0.8
        return frame.clip(0, 255).astype(np.uint8)

    video = VideoClip(make_frame, duration=duration).set_audio(audio)
    # Render to a temp name so a half-written file is never mistaken for the result.
    tmp_path = Path(video_path).with_suffix(".rendering.mp4")
    video.write_videofile(
        str(tmp_path), fps=FPS, codec="libx264", audio_codec="aac", audio_bitrate="128k",
        temp_audiofile=str(Path(audio_path).with_suffix(".tmp.m4a")),
        preset="veryfast", threads=os.cpu_count(), ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
        logger=None,
    )
    video.close()
    audio.close()
    for scene in scenes:
        scene.close()
    os.replace(tmp_path, video_path)
    return str(video_path)
