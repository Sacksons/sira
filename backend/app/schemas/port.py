"""
Port & Terminal Schemas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


# Port schemas
class PortBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(..., min_length=1, max_length=100)
    region: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    port_type: Optional[str] = None
    max_draft: Optional[float] = None
    max_loa: Optional[float] = None
    anchorage_capacity: Optional[int] = None


class PortCreate(PortBase):
    authority: Optional[str] = None
    timezone: Optional[str] = None
    notes: Optional[str] = None


class PortUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, pattern="^(operational|congested|closed|restricted)$")
    current_queue: Optional[int] = None
    avg_wait_days: Optional[float] = None
    avg_dwell_days: Optional[float] = None
    notes: Optional[str] = None


class PortResponse(PortBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    current_queue: int
    avg_wait_days: float
    avg_dwell_days: float
    authority: Optional[str] = None
    timezone: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Berth schemas
class BerthBase(BaseModel):
    port_id: int
    name: str = Field(..., min_length=1, max_length=255)
    berth_type: Optional[str] = None
    max_draft: Optional[float] = None
    max_loa: Optional[float] = None
    max_beam: Optional[float] = None
    cargo_types: Optional[str] = None
    equipment: Optional[str] = None
    loading_rate: Optional[float] = None


class BerthCreate(BerthBase):
    pass


class BerthUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, pattern="^(available|occupied|maintenance|reserved)$")
    loading_rate: Optional[float] = None
    equipment: Optional[str] = None


class BerthResponse(BerthBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None


# Berth Booking schemas
class BerthBookingBase(BaseModel):
    berth_id: int
    vessel_id: int
    shipment_id: Optional[int] = None
    scheduled_arrival: datetime
    scheduled_departure: datetime
    cargo_type: Optional[str] = None
    cargo_volume: Optional[float] = None
    priority: int = 5


class BerthBookingCreate(BerthBookingBase):
    pass


class BerthBookingUpdate(BaseModel):
    scheduled_arrival: Optional[datetime] = None
    scheduled_departure: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    actual_departure: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(scheduled|confirmed|active|completed|cancelled)$")
    priority: Optional[int] = None


class BerthBookingResponse(BerthBookingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    actual_arrival: Optional[datetime] = None
    actual_departure: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
