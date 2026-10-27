from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.utils import utcnow

class VideoJob(Base):
    __tablename__ = "video_jobs"
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    status = Column(String(50), default="queued", index=True)
    script = Column(Text, default="")
    video_path = Column(String(1500), default="")
    retry_count = Column(Integer, default=0)
    youtube_video_id = Column(String(100), default="")
    youtube_url = Column(String(500), default="")
    error = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=utcnow)
    article = relationship("Article", back_populates="jobs")
    reviews = relationship("VideoReview", back_populates="job", cascade="all, delete-orphan")
