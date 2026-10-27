from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.utils import utcnow

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    # 768 chars is the longest unique index MySQL allows with utf8mb4 (3072 bytes).
    url = Column(String(768), unique=True, nullable=False, index=True)
    source = Column(String(300), default="")
    summary = Column(Text, default="")
    content = Column(Text, default="")
    published_at = Column(String(100), default="")
    score = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    jobs = relationship("VideoJob", back_populates="article")
