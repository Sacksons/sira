"""
IoT Device & Telemetry Schemas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class IoTDeviceBase(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=100)
    device_type: str = Field(..., min_length=1, max_length=100)
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None


class IoTDeviceCreate(IoTDeviceBase):
    asset_id: Optional[int] = None
    vessel_id: Optional[int] = None
    installation_location: Optional[str] = None
    reporting_interval_sec: int = 300


class IoTDeviceUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(active|offline|maintenance|decommissioned)$")
    firmware_version: Optional[str] = None
    asset_id: Optional[int] = None
    vessel_id: Optional[int] = None
    reporting_interval_sec: Optional[int] = None
    alert_thresholds: Optional[str] = None


class IoTDeviceResponse(IoTDeviceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: Optional[int] = None
    vessel_id: Optional[int] = None
    shipment_id: Optional[int] = None
    installation_location: Optional[str] = None
    status: str
    battery_level: Optional[float] = None
    signal_strength: Optional[float] = None
    last_seen: Optional[datetime] = None
    last_lat: Optional[float] = None
    last_lng: Optional[float] = None
    reporting_interval_sec: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# Telemetry schemas
class TelemetryCreate(BaseModel):
    device_id: int
    timestamp: datetime
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    altitude: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    weight: Optional[float] = None
    fuel_level: Optional[float] = None
    battery_level: Optional[float] = None
    vibration: Optional[float] = None
    seal_intact: Optional[bool] = None
    raw_payload: Optional[str] = None


class TelemetryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    timestamp: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    weight: Optional[float] = None
    fuel_level: Optional[float] = None
    battery_level: Optional[float] = None
    vibration: Optional[float] = None
    seal_intact: Optional[bool] = None
    created_at: datetime
