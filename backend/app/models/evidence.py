"""
Evidence Model - Case evidence with integrity tracking
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class Evidence(Base):
    __tablename__ = "evidences"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(
        Integer,
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    evidence_type = Column(
        String(50),
        nullable=False
    )  # IoT, photo, video, document, audio, log
    file_ref = Column(String(500))  # S3 path or local reference
    original_filename = Column(String(255))
    file_size = Column(Integer)  # bytes
    mime_type = Column(String(100))
    evidence_metadata = Column(Text)  # JSON: uploader, timestamp, location, device
    verification_status = Column(
        String(50),
        default="pending"
    )  # pending, verified, rejected
    file_hash = Column(String(64))  # SHA-256 for integrity
    blockchain_hash = Column(String(100))  # For future blockchain anchoring
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    case = relationship("Case", back_populates="evidences")

    def __repr__(self):
        return f"<Evidence(id={self.id}, type='{self.evidence_type}', case_id={self.case_id})>"
