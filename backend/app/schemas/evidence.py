"""
Evidence Schemas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class EvidenceBase(BaseModel):
    """Base evidence schema"""
    case_id: int = Field(..., gt=0)
    evidence_type: str = Field(..., max_length=50)
    file_ref: str = Field(..., max_length=500)
    original_filename: Optional[str] = Field(None, max_length=255)
    metadata: Optional[str] = None
    notes: Optional[str] = None


class EvidenceCreate(EvidenceBase):
    """Schema for creating evidence"""
    pass


class EvidenceResponse(EvidenceBase):
    """Schema for evidence response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    verification_status: str
    file_hash: Optional[str] = None
    blockchain_hash: Optional[str] = None
    uploaded_by: Optional[int] = None
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    created_at: datetime


class EvidenceVerify(BaseModel):
    """Schema for verifying evidence"""
    status: str = Field(
        ...,
        pattern="^(verified|rejected)$"
    )
    notes: Optional[str] = None
