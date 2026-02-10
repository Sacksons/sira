"""
Shipment Schemas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class ShipmentBase(BaseModel):
    shipment_ref: str = Field(..., min_length=1, max_length=50)
    corridor_id: Optional[int] = None
    vessel_id: Optional[int] = None
    cargo_type: str = Field(..., min_length=1, max_length=100)
    cargo_grade: Optional[str] = None
    volume_tonnes: Optional[float] = None
    bill_of_lading: Optional[str] = None
    origin: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    origin_port_id: Optional[int] = None
    destination_port_id: Optional[int] = None
    laycan_start: datetime
    laycan_end: datetime
    demurrage_rate_usd: Optional[float] = None
    shipper: Optional[str] = None
    receiver: Optional[str] = None
    freight_forwarder: Optional[str] = None
    insurance_ref: Optional[str] = None


class ShipmentCreate(ShipmentBase):
    pass


class ShipmentUpdate(BaseModel):
    vessel_id: Optional[int] = None
    status: Optional[str] = Field(None, pattern="^(planned|loading|in_transit|at_port|discharging|completed|cancelled)$")
    current_leg: Optional[str] = None
    current_mode: Optional[str] = None
    eta_destination: Optional[datetime] = None
    eta_confidence: Optional[float] = Field(None, ge=0, le=1)
    demurrage_risk_score: Optional[float] = Field(None, ge=0, le=100)
    demurrage_exposure_usd: Optional[float] = None
    loading_started: Optional[datetime] = None
    loading_completed: Optional[datetime] = None
    departed_origin: Optional[datetime] = None
    arrived_destination: Optional[datetime] = None
    discharge_started: Optional[datetime] = None
    discharge_completed: Optional[datetime] = None
    freight_cost: Optional[float] = None
    insurance_cost: Optional[float] = None
    total_cost: Optional[float] = None


class ShipmentResponse(ShipmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    current_leg: Optional[str] = None
    current_mode: Optional[str] = None
    eta_destination: Optional[datetime] = None
    eta_confidence: Optional[float] = None
    eta_updated_at: Optional[datetime] = None
    demurrage_risk_score: float
    demurrage_exposure_usd: float
    demurrage_days: float
    loading_started: Optional[datetime] = None
    loading_completed: Optional[datetime] = None
    departed_origin: Optional[datetime] = None
    arrived_destination: Optional[datetime] = None
    discharge_started: Optional[datetime] = None
    discharge_completed: Optional[datetime] = None
    custody_seal_id: Optional[str] = None
    custody_status: str
    freight_cost: Optional[float] = None
    insurance_cost: Optional[float] = None
    total_cost: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Milestone schemas
class MilestoneCreate(BaseModel):
    shipment_id: int
    milestone_type: str = Field(..., min_length=1)
    description: Optional[str] = None
    location: Optional[str] = None
    mode: Optional[str] = None
    planned_time: Optional[datetime] = None
    actual_time: Optional[datetime] = None


class MilestoneUpdate(BaseModel):
    actual_time: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(pending|completed|skipped|delayed)$")


class MilestoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shipment_id: int
    milestone_type: str
    description: Optional[str] = None
    location: Optional[str] = None
    mode: Optional[str] = None
    planned_time: Optional[datetime] = None
    actual_time: Optional[datetime] = None
    variance_hours: Optional[float] = None
    status: str
    created_at: datetime


# Custody Event schemas
class CustodyEventCreate(BaseModel):
    shipment_id: int
    event_type: str = Field(..., min_length=1)
    location: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    from_party: Optional[str] = None
    to_party: Optional[str] = None
    witnessed_by: Optional[str] = None
    seal_number: Optional[str] = None
    seal_status: Optional[str] = None
    measured_volume: Optional[float] = None
    expected_volume: Optional[float] = None
    photo_ref: Optional[str] = None
    document_ref: Optional[str] = None
    notes: Optional[str] = None


class CustodyEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shipment_id: int
    event_type: str
    timestamp: datetime
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    from_party: Optional[str] = None
    to_party: Optional[str] = None
    witnessed_by: Optional[str] = None
    seal_number: Optional[str] = None
    seal_status: Optional[str] = None
    measured_volume: Optional[float] = None
    expected_volume: Optional[float] = None
    volume_variance_pct: Optional[float] = None
    photo_ref: Optional[str] = None
    document_ref: Optional[str] = None
    digital_signature: Optional[str] = None
    blockchain_tx: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime


# Shipment Document schemas
class DocumentCreate(BaseModel):
    shipment_id: int
    document_type: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    file_ref: Optional[str] = None
    issued_by: Optional[str] = None
    issued_at: Optional[datetime] = None
    notes: Optional[str] = None


class DocumentUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(pending|verified|rejected|expired)$")
    notes: Optional[str] = None


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shipment_id: int
    document_type: str
    title: str
    file_ref: Optional[str] = None
    file_hash: Optional[str] = None
    status: str
    issued_by: Optional[str] = None
    issued_at: Optional[datetime] = None
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Exception schemas
class ExceptionCreate(BaseModel):
    shipment_id: int
    exception_type: str = Field(..., min_length=1)
    severity: str = Field(..., pattern="^(critical|high|medium|low)$")
    description: Optional[str] = None
    impact_description: Optional[str] = None
    estimated_delay_hours: Optional[float] = None
    estimated_cost_usd: Optional[float] = None


class ExceptionUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(open|acknowledged|mitigating|resolved)$")
    resolution: Optional[str] = None


class ExceptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shipment_id: int
    exception_type: str
    severity: str
    description: Optional[str] = None
    impact_description: Optional[str] = None
    estimated_delay_hours: Optional[float] = None
    estimated_cost_usd: Optional[float] = None
    status: str
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    ai_recommendation: Optional[str] = None
    ai_confidence: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ShipmentDetailResponse(ShipmentResponse):
    milestones: List[MilestoneResponse] = []
    custody_events: List[CustodyEventResponse] = []
    documents: List[DocumentResponse] = []
    exceptions: List[ExceptionResponse] = []
