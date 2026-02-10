"""
Fleet & Asset Schemas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class AssetBase(BaseModel):
    asset_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    asset_type: str = Field(..., min_length=1, max_length=50)
    sub_type: Optional[str] = None
    owner: Optional[str] = None
    operator: Optional[str] = None
    capacity: Optional[float] = None
    max_payload: Optional[float] = None
    fuel_type: Optional[str] = None
    year_manufactured: Optional[int] = None
    registration: Optional[str] = None


class AssetCreate(AssetBase):
    iot_device_id: Optional[str] = None


class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, pattern="^(available|in_transit|loading|unloading|maintenance|breakdown|idle)$")
    current_location: Optional[str] = None
    current_lat: Optional[float] = Field(None, ge=-90, le=90)
    current_lng: Optional[float] = Field(None, ge=-180, le=180)
    assigned_corridor_id: Optional[int] = None
    assigned_shipment_id: Optional[int] = None
    maintenance_status: Optional[str] = None
    next_maintenance: Optional[datetime] = None


class AssetResponse(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    current_location: Optional[str] = None
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    current_speed: Optional[float] = None
    assigned_corridor_id: Optional[int] = None
    assigned_shipment_id: Optional[int] = None
    utilization_pct: float
    total_trips: int
    total_distance_km: float
    last_trip_end: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    maintenance_status: str
    iot_device_id: Optional[str] = None
    last_telemetry_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Dispatch Record schemas
class DispatchCreate(BaseModel):
    asset_id: int
    shipment_id: Optional[int] = None
    origin: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    dispatched_at: datetime
    estimated_arrival: Optional[datetime] = None
    cargo_type: Optional[str] = None
    cargo_volume: Optional[float] = None
    driver_name: Optional[str] = None
    driver_contact: Optional[str] = None
    notes: Optional[str] = None


class DispatchUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(dispatched|in_transit|arrived|completed|cancelled)$")
    actual_arrival: Optional[datetime] = None
    notes: Optional[str] = None


class DispatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    shipment_id: Optional[int] = None
    origin: str
    destination: str
    dispatched_at: datetime
    estimated_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    cargo_type: Optional[str] = None
    cargo_volume: Optional[float] = None
    status: str
    driver_name: Optional[str] = None
    driver_contact: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Maintenance Record schemas
class MaintenanceCreate(BaseModel):
    asset_id: Optional[int] = None
    vessel_id: Optional[int] = None
    maintenance_type: str = Field(..., min_length=1)
    description: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    cost: Optional[float] = None
    vendor: Optional[str] = None


class MaintenanceUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(scheduled|in_progress|completed|cancelled)$")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cost: Optional[float] = None
    notes: Optional[str] = None


class MaintenanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: Optional[int] = None
    vessel_id: Optional[int] = None
    maintenance_type: str
    description: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cost: float
    vendor: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
