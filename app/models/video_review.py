from sqlalchemy import Column, Integer, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.utils import utcnow

class VideoReview(Base):
    __tablename__ = "video_reviews"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("video_jobs.id"), nullable=False)
    approved = Column(Boolean, default=False)
    score = Column(Float, default=0)
    issues = Column(Text, default="")
    feedback = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=utcnow)
    job = relationship("VideoJob", back_populates="reviews")
