from pydantic import BaseModel, ConfigDict

class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    article_id: int
    status: str
    video_path: str
    retry_count: int
    youtube_video_id: str
    youtube_url: str
    error: str
