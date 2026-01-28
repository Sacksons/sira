"""
Movement Model - Shipping cargo movement tracking
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class Movement(Base):
    __tablename__ = "movements"

    id = Column(Integer, primary_key=True, index=True)
    cargo = Column(String(255), nullable=False)
    route = Column(Text, nullable=False)
    assets = Column(Text)  # JSON: vessels, vehicles, containers
    stakeholders = Column(Text)  # JSON: shippers, receivers, agents
    laycan_start = Column(DateTime(timezone=True), nullable=False)
    laycan_end = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), default="active", index=True)
    current_location = Column(String(255))
    current_lat = Column(Float, nullable=True)
    current_lng = Column(Float, nullable=True)
    risk_score = Column(Float, default=0.0)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    events = relationship(
        "Event",
        back_populates="movement",
        cascade="all, delete-orphan"
    )
    alerts = relationship("Alert", back_populates="movement")

    def __repr__(self):
        return f"<Movement(id={self.id}, cargo='{self.cargo}', status='{self.status}')>"
