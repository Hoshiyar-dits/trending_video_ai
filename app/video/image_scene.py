import numpy as np
from PIL import Image

from app.video.constants import W, H, MAX_ZOOM
from app.video.utils import smooth

class ImageScene:
    MOTIONS = ("zoom_in", "zoom_out", "pan_left", "pan_right")

    def __init__(self, image, motion, rng):
        self.image = image
        self.motion = motion
        # Random focal points so a reused photo shows a different part of the frame.
        self.focus = [(rng.uniform(0.3, 0.7), rng.uniform(0.35, 0.65)) for _ in range(2)]

    def frame(self, p, t_local):
        p = smooth(min(max(p, 0.0), 1.0))
        iw, ih = self.image.size
        if self.motion == "zoom_in":
            zoom = 1 + (MAX_ZOOM - 1) * p
        elif self.motion == "zoom_out":
            zoom = MAX_ZOOM - (MAX_ZOOM - 1) * p
        else:
            zoom = 1.08
        bh = ih / zoom
        bw = bh * W / H
        (fx0, fy0), (fx1, fy1) = self.focus
        if self.motion == "pan_left":
            fx0, fx1 = 0.0, 1.0
        elif self.motion == "pan_right":
            fx0, fx1 = 1.0, 0.0
        fx = fx0 + (fx1 - fx0) * p
        fy = fy0 + (fy1 - fy0) * p
        x0 = (iw - bw) * fx
        y0 = (ih - bh) * fy
        box = (x0, y0, x0 + bw, y0 + bh)
        return np.asarray(self.image.resize((W, H), Image.BILINEAR, box=box), dtype=np.float32)

    def close(self):
        pass
