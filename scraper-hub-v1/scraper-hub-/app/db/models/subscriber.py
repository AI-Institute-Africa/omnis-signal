from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.db.base import Base


class ReportSubscriber(Base):
    """Subscribers registered in the system to receive automated price & tariff reports."""
    __tablename__ = "report_subscribers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    organization = Column(String(255), nullable=True)
    role = Column(String(100), nullable=True)
    frequency = Column(String(50), default="4h")  # "4h", "daily", "weekly"
    sector_filter = Column(String(255), default="all")  # "all" or comma-separated sectors
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "organization": self.organization,
            "role": self.role,
            "frequency": self.frequency,
            "sector_filter": self.sector_filter,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
