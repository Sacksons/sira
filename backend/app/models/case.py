"""
Case Model - Incident investigation cases
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(50), unique=True, index=True)  # Auto-generated
    title = Column(String(255), nullable=False)
    overview = Column(Text)
    timeline = Column(Text)  # JSON of events
    actions = Column(Text)  # JSON of actions taken
    evidence_refs = Column(Text)  # JSON of evidence references
    costs = Column(Float, default=0.0)
    parties = Column(Text)  # JSON of involved parties
    audit = Column(Text)  # JSON audit trail
    status = Column(String(50), default="open", index=True)
    closure_code = Column(String(100))
    priority = Column(String(20), default="medium", index=True)
    category = Column(String(100))  # theft, delay, damage, etc.
    assigned_to = Column(Integer, nullable=True)
    created_by = Column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    alerts = relationship("Alert", back_populates="case")
    evidences = relationship(
        "Evidence",
        back_populates="case",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Case(id={self.id}, case_number='{self.case_number}', status='{self.status}')>"
