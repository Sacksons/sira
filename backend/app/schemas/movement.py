"""
Movement Schemas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class MovementBase(BaseModel):
    """Base movement schema"""
    cargo: str = Field(..., min_length=1, max_length=255)
    route: str = Field(..., min_length=1)
    assets: Optional[str] = None
    stakeholders: Optional[str] = None
    laycan_start: datetime
    laycan_end: datetime


class MovementCreate(MovementBase):
    """Schema for creating a movement"""
    pass


class MovementUpdate(BaseModel):
    """Schema for updating a movement"""
    cargo: Optional[str] = Field(None, min_length=1, max_length=255)
    route: Optional[str] = None
    assets: Optional[str] = None
    stakeholders: Optional[str] = None
    status: Optional[str] = Field(
        None,
        pattern="^(active|completed|cancelled|delayed)$"
    )
    current_location: Optional[str] = None
    current_lat: Optional[float] = Field(None, ge=-90, le=90)
    current_lng: Optional[float] = Field(None, ge=-180, le=180)
    risk_score: Optional[float] = Field(None, ge=0, le=100)


class MovementResponse(MovementBase):
    """Schema for movement response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    current_location: Optional[str] = None
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    risk_score: float
    created_at: datetime
    updated_at: Optional[datetime] = None


class MovementWithEvents(MovementResponse):
    """Movement response with events"""
    events: List["EventResponse"] = []


# Forward reference for circular import
from app.schemas.event import EventResponse
MovementWithEvents.model_rebuild()
