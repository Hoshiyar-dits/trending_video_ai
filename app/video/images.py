import io
import math
import random
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFilter

from app.video.constants import W, H, MAX_ZOOM, USER_AGENT

def fetch_article_images(url, limit=4, min_width=600):
    """Download the article's lead image (og:image) plus photos from the article body."""
    if not url:
        return []
    try:
        html = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15).text
    except requests.RequestException:
        return []

    candidates = re.findall(
        r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\'][^>]+content=["\']([^"\']+)', html
    )
    body = re.search(r"<article.*?</article>", html, re.S)
    for tag in re.findall(r"<img[^>]+>", body.group(0) if body else html):
        srcset = re.search(r'srcset=["\']([^"\']+)', tag)
        if srcset:
            # Take the largest entry of the srcset.
            candidates.append(srcset.group(1).split(",")[-1].strip().split(" ")[0])
        else:
            src = re.search(r'src=["\']([^"\']+)', tag)
            if src:
                candidates.append(src.group(1))

    images, seen = [], set()
    for candidate in candidates:
        full = urljoin(url, candidate.replace("&amp;", "&"))
        # The same photo is often listed at several sizes; dedupe on its file name.
        key = Path(urlparse(full).path).name.split(".")[0]
        if key in seen or full.startswith("data:"):
            continue
        seen.add(key)
        try:
            response = requests.get(full, headers={"User-Agent": USER_AGENT}, timeout=15)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
        except Exception:
            continue
        if image.width >= min_width:
            images.append(image)
        if len(images) >= limit:
            break
    return images

def fallback_background(seed):
    """Abstract gradient with soft colour blobs, used when the article has no usable photo."""
    rng = random.Random(seed)
    w, h = int(W * 1.6), int(H * 1.6)
    y = np.linspace(0, 1, h)[:, None, None]
    top, bottom = np.array([14, 24, 52]), np.array([40, 12, 60])
    base = Image.fromarray((top * (1 - y) + bottom * y).repeat(w, axis=1).astype(np.uint8))
    blobs = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(blobs)
    for _ in range(7):
        r = rng.randint(150, 380)
        cx, cy = rng.randint(0, w), rng.randint(0, h)
        color = rng.choice([(0, 170, 255), (255, 70, 140), (120, 80, 255), (0, 220, 180)])
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
    blobs = blobs.filter(ImageFilter.GaussianBlur(120))
    return Image.blend(base, blobs, 0.55)

def cover_image(image):
    """Scale so a W x H window can zoom up to MAX_ZOOM and still have room to pan."""
    scale = max(W * MAX_ZOOM * 1.1 / image.width, H * MAX_ZOOM / image.height)
    return image.resize((math.ceil(image.width * scale), math.ceil(image.height * scale)), Image.LANCZOS)
