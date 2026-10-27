from PIL import ImageFont

from app.video.constants import FONT_PATH

def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        return ImageFont.load_default()

def smooth(p):
    return p * p * (3 - 2 * p)
