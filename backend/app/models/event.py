"""
Event Model - Timeline events for movements
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    movement_id = Column(
        Integer,
        ForeignKey("movements.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    location = Column(String(255))
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    actor = Column(String(255))
    evidence = Column(Text)  # JSON reference to evidence
    event_type = Column(
        String(50),
        nullable=False,
        index=True
    )  # planned, actual, security, operational
    severity = Column(String(20), default="info")  # info, warning, critical
    description = Column(Text)
    event_metadata = Column(Text)  # JSON for additional data
    source = Column(String(100))  # iot, manual, ais, satellite
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    movement = relationship("Movement", back_populates="events")

    def __repr__(self):
        return f"<Event(id={self.id}, type='{self.event_type}', movement_id={self.movement_id})>"
