
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", BASE_DIR / "storage"))
AUDIO_DIR = STORAGE_DIR / "audio"
VIDEO_DIR = STORAGE_DIR / "videos"

# MySQL only (async driver), e.g. mysql+aiomysql://user:password@localhost:3306/trending_video_ai
DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL.startswith("mysql+aiomysql://"):
    raise RuntimeError(
        "DATABASE_URL must be a MySQL URL like "
        "mysql+aiomysql://user:password@localhost:3306/trending_video_ai"
    )
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
RSS_FEEDS = [x.strip() for x in os.getenv(
    "RSS_FEEDS",
    "https://feeds.bbci.co.uk/news/technology/rss.xml"
).split(",") if x.strip()]
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
YOUTUBE_PUBLIC_PUBLISHING_ENABLED = os.getenv(
    "YOUTUBE_PUBLIC_PUBLISHING_ENABLED", "false"
).lower() == "true"
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
YOUTUBE_PRIVACY_STATUS =os.getenv("YOUTUBE_PRIVACY_STATUS", "private")
YOUTUBE_CLIENT_SECRETS = os.getenv("YOUTUBE_CLIENT_SECRETS", "client_secret.json")
YOUTUBE_TOKEN_FILE = os.getenv("YOUTUBE_TOKEN_FILE", "youtube_token.json")

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
VIDEO_DIR.mkdir(parents=True, exist_ok=True)