import numpy as np
from moviepy.editor import VideoFileClip

class VideoScene:
    """A stock clip already cropped to W x H; loops if shorter than the scene."""

    def __init__(self, path):
        self.clip = VideoFileClip(str(path), audio=False)

    def frame(self, p, t_local):
        t = t_local % max(self.clip.duration - 0.1, 0.1)
        return self.clip.get_frame(t).astype(np.float32)

    def close(self):
        self.clip.close()
