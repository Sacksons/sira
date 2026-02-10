"""
Vessel Schemas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class VesselBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    imo_number: str = Field(..., min_length=1, max_length=20)
    mmsi: Optional[str] = Field(None, max_length=20)
    vessel_type: str = Field(..., min_length=1, max_length=100)
    flag: Optional[str] = None
    dwt: Optional[float] = None
    loa: Optional[float] = None
    beam: Optional[float] = None
    draft: Optional[float] = None
    year_built: Optional[int] = None
    owner: Optional[str] = None
    operator: Optional[str] = None
    class_society: Optional[str] = None


class VesselCreate(VesselBase):
    charter_type: Optional[str] = None
    charter_rate: Optional[float] = None
    charter_start: Optional[datetime] = None
    charter_end: Optional[datetime] = None


class VesselUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    vessel_type: Optional[str] = None
    flag: Optional[str] = None
    dwt: Optional[float] = None
    draft: Optional[float] = None
    owner: Optional[str] = None
    operator: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|idle|maintenance|drydock|decommissioned)$")
    current_lat: Optional[float] = Field(None, ge=-90, le=90)
    current_lng: Optional[float] = Field(None, ge=-180, le=180)
    current_speed: Optional[float] = None
    current_heading: Optional[float] = None
    current_destination: Optional[str] = None
    charter_type: Optional[str] = None
    charter_rate: Optional[float] = None
    charter_start: Optional[datetime] = None
    charter_end: Optional[datetime] = None


class VesselPositionUpdate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    speed: Optional[float] = None
    heading: Optional[float] = None
    destination: Optional[str] = None
    ais_status: Optional[str] = None


class VesselResponse(VesselBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    ais_status: Optional[str] = None
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    current_speed: Optional[float] = None
    current_heading: Optional[float] = None
    current_destination: Optional[str] = None
    position_updated_at: Optional[datetime] = None
    charter_type: Optional[str] = None
    charter_rate: Optional[float] = None
    charter_start: Optional[datetime] = None
    charter_end: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
