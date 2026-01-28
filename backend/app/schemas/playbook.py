"""
Playbook Schemas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class PlaybookBase(BaseModel):
    """Base playbook schema"""
    incident_type: str = Field(..., min_length=1, max_length=100)
    domain: Optional[str] = Field(None, max_length=100)
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    steps: str  # JSON string of steps
    estimated_duration: Optional[int] = Field(None, gt=0)  # minutes
    required_roles: Optional[str] = None  # JSON array
    escalation_rules: Optional[str] = None  # JSON


class PlaybookCreate(PlaybookBase):
    """Schema for creating a playbook"""
    pass


class PlaybookUpdate(BaseModel):
    """Schema for updating a playbook"""
    incident_type: Optional[str] = Field(None, min_length=1, max_length=100)
    domain: Optional[str] = Field(None, max_length=100)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    steps: Optional[str] = None
    estimated_duration: Optional[int] = Field(None, gt=0)
    required_roles: Optional[str] = None
    escalation_rules: Optional[str] = None
    is_active: Optional[bool] = None


class PlaybookResponse(PlaybookBase):
    """Schema for playbook response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    version: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
