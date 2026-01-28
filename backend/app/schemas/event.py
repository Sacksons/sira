"""
Event Schemas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class EventBase(BaseModel):
    """Base event schema"""
    movement_id: int = Field(..., gt=0)
    timestamp: datetime
    location: Optional[str] = Field(None, max_length=255)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    actor: Optional[str] = Field(None, max_length=255)
    evidence: Optional[str] = None
    event_type: str = Field(
        ...,
        pattern="^(planned|actual|security|operational)$"
    )
    severity: str = Field(
        default="info",
        pattern="^(info|warning|critical)$"
    )
    description: Optional[str] = None
    metadata: Optional[str] = None
    source: Optional[str] = Field(None, max_length=100)


class EventCreate(EventBase):
    """Schema for creating an event"""
    pass


class EventResponse(EventBase):
    """Schema for event response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
