"""
Alert Model - Security alerts with SLA tracking
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    severity = Column(String(20), nullable=False, index=True)  # Critical/High/Medium/Low
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    sla_timer = Column(Integer)  # minutes until SLA breach
    sla_breached = Column(Boolean, default=False)
    domain = Column(String(100), index=True)  # security, compliance, operational
    site_zone = Column(String(100))
    movement_id = Column(Integer, ForeignKey("movements.id"), nullable=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    status = Column(
        String(50),
        default="open",
        index=True
    )  # open/acknowledged/assigned/investigating/closed
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    description = Column(Text)
    rule_id = Column(String(100))  # ID of the rule that triggered this alert
    rule_name = Column(String(255))  # Name of the triggering rule
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    movement = relationship("Movement", back_populates="alerts")
    case = relationship("Case", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(id={self.id}, severity='{self.severity}', status='{self.status}')>"
