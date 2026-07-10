from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class RawSnapshot(Base):
    __tablename__ = "raw_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    source_page_id = Column(Integer, ForeignKey("source_pages.id"), nullable=True)
    url = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String, nullable=False)  # html, pdf, etc.
    captured_at = Column(DateTime(timezone=True), server_default=func.now())

    records = relationship("ExtractedRecord", back_populates="snapshot")