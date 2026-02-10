"""
Corridor Schemas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class CorridorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    corridor_type: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    description: Optional[str] = None
    origin_port_id: Optional[int] = None
    destination_port_id: Optional[int] = None
    waypoints: Optional[str] = None
    total_distance_km: Optional[float] = None
    modes: Optional[str] = None
    primary_commodity: Optional[str] = None
    annual_volume_mt: Optional[float] = None


class CorridorCreate(CorridorBase):
    pass


class CorridorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, pattern="^(active|seasonal|disrupted|closed)$")
    description: Optional[str] = None
    avg_transit_days: Optional[float] = None
    avg_demurrage_days: Optional[float] = None
    avg_cost_per_tonne: Optional[float] = None


class CorridorResponse(CorridorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    avg_transit_days: Optional[float] = None
    avg_demurrage_days: Optional[float] = None
    avg_cost_per_tonne: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Geofence schemas
class GeofenceBase(BaseModel):
    corridor_id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=255)
    fence_type: Optional[str] = None
    geometry: str = Field(..., min_length=1)
    alert_on_enter: bool = True
    alert_on_exit: bool = True
    alert_on_dwell: bool = False
    max_dwell_minutes: Optional[int] = None


class GeofenceCreate(GeofenceBase):
    pass


class GeofenceUpdate(BaseModel):
    name: Optional[str] = None
    geometry: Optional[str] = None
    is_active: Optional[bool] = None
    alert_on_enter: Optional[bool] = None
    alert_on_exit: Optional[bool] = None
    alert_on_dwell: Optional[bool] = None
    max_dwell_minutes: Optional[int] = None


class GeofenceResponse(GeofenceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
