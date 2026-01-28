"""
Playbook Model - Standardized incident response procedures
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime, timezone

from app.core.database import Base


class Playbook(Base):
    __tablename__ = "playbooks"

    id = Column(Integer, primary_key=True, index=True)
    incident_type = Column(String(100), nullable=False, index=True)
    domain = Column(String(100), index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    steps = Column(Text, nullable=False)  # JSON array of steps
    estimated_duration = Column(Integer)  # minutes
    required_roles = Column(Text)  # JSON array of roles
    escalation_rules = Column(Text)  # JSON escalation criteria
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    created_by = Column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Playbook(id={self.id}, title='{self.title}', incident_type='{self.incident_type}')>"
