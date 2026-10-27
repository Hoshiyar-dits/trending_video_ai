import re

import numpy as np
from PIL import Image, ImageDraw

from app.video.constants import W

def split_scenes(script, target_chars=90):
    """Group whole sentences into scenes of roughly 6 seconds of narration."""
    scenes, current = [], ""
    for sentence in re.split(r"(?<=[.!?])\s+", script.strip()):
        current = f"{current} {sentence}".strip()
        if len(current) >= target_chars:
            scenes.append(current)
            current = ""
    if current:
        if scenes and len(current) < target_chars / 2:
            scenes[-1] = f"{scenes[-1]} {current}"
        else:
            scenes.append(current)
    return scenes or [script]

def caption_chunks(script, max_words=6):
    chunks = []
    for sentence in re.split(r"(?<=[.!?;:])\s+", script.strip()):
        words = sentence.split()
        for i in range(0, len(words), max_words):
            chunks.append(" ".join(words[i:i + max_words]))
    return [c for c in chunks if c]

def chunk_weight(chunk):
    return len(chunk) + (12 if chunk[-1] in ".!?;:," else 0)

def caption_timings(chunks, duration):
    # espeak-ng speaks at a near-constant rate and pauses on punctuation,
    # so character count is a good proxy for when each chunk is spoken.
    weights = [chunk_weight(c) for c in chunks]
    total = sum(weights) or 1
    timings, t = [], 0.0
    for chunk, weight in zip(chunks, weights):
        span = duration * weight / total
        timings.append((t, t + span, chunk))
        t += span
    return timings

def render_caption(text, font):
    draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] > W - 120:
            lines.append(current)
            current = word
        else:
            current = candidate
    lines.append(current)
    line_h = font.size + 14
    layer = Image.new("RGBA", (W, line_h * len(lines) + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i, line in enumerate(lines):
        lw = d.textbbox((0, 0), line, font=font)[2]
        d.text(((W - lw) / 2, 10 + i * line_h), line, font=font, fill="white",
               stroke_width=4, stroke_fill="black")
    rgba = np.asarray(layer, dtype=np.float32)
    return rgba[..., :3], rgba[..., 3:] / 255.0
