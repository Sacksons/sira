"""
Freight Rate & Market Intelligence Schemas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


# Freight Rate schemas
class FreightRateBase(BaseModel):
    corridor_id: Optional[int] = None
    lane: str = Field(..., min_length=1, max_length=255)
    mode: str = Field(..., min_length=1, max_length=50)
    cargo_type: Optional[str] = None
    rate_usd: float = Field(..., gt=0)
    rate_unit: str = Field(..., min_length=1, max_length=50)
    currency: str = "USD"
    rate_type: Optional[str] = None
    source: Optional[str] = None
    effective_date: datetime
    expiry_date: Optional[datetime] = None


class FreightRateCreate(FreightRateBase):
    vessel_class: Optional[str] = None
    vessel_size_dwt_min: Optional[float] = None
    vessel_size_dwt_max: Optional[float] = None
    fuel_surcharge: Optional[float] = None
    port_charges: Optional[float] = None
    total_cost: Optional[float] = None


class FreightRateResponse(FreightRateBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vessel_class: Optional[str] = None
    vessel_size_dwt_min: Optional[float] = None
    vessel_size_dwt_max: Optional[float] = None
    fuel_surcharge: Optional[float] = None
    port_charges: Optional[float] = None
    total_cost: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Market Index schemas
class MarketIndexCreate(BaseModel):
    index_name: str = Field(..., min_length=1, max_length=255)
    index_type: Optional[str] = None
    value: float
    unit: Optional[str] = None
    change_pct: Optional[float] = None
    change_abs: Optional[float] = None
    period: Optional[str] = None
    source: Optional[str] = None
    recorded_at: datetime


class MarketIndexResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    index_name: str
    index_type: Optional[str] = None
    value: float
    unit: Optional[str] = None
    change_pct: Optional[float] = None
    change_abs: Optional[float] = None
    period: Optional[str] = None
    source: Optional[str] = None
    recorded_at: datetime
    created_at: datetime


# Demurrage Record schemas
class DemurrageCreate(BaseModel):
    shipment_id: int
    vessel_id: Optional[int] = None
    port_id: Optional[int] = None
    laycan_start: Optional[datetime] = None
    laycan_end: Optional[datetime] = None
    nor_tendered: Optional[datetime] = None
    laytime_allowed_hours: Optional[float] = None
    demurrage_rate_usd: Optional[float] = None


class DemurrageUpdate(BaseModel):
    laytime_start: Optional[datetime] = None
    laytime_end: Optional[datetime] = None
    laytime_used_hours: Optional[float] = None
    demurrage_start: Optional[datetime] = None
    demurrage_end: Optional[datetime] = None
    demurrage_days: Optional[float] = None
    demurrage_amount_usd: Optional[float] = None
    despatch_days: Optional[float] = None
    despatch_amount_usd: Optional[float] = None
    status: Optional[str] = Field(None, pattern="^(accruing|calculated|disputed|settled)$")
    notes: Optional[str] = None


class DemurrageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shipment_id: int
    vessel_id: Optional[int] = None
    port_id: Optional[int] = None
    laycan_start: Optional[datetime] = None
    laycan_end: Optional[datetime] = None
    nor_tendered: Optional[datetime] = None
    laytime_start: Optional[datetime] = None
    laytime_end: Optional[datetime] = None
    laytime_allowed_hours: Optional[float] = None
    laytime_used_hours: Optional[float] = None
    demurrage_start: Optional[datetime] = None
    demurrage_end: Optional[datetime] = None
    demurrage_days: Optional[float] = None
    demurrage_rate_usd: Optional[float] = None
    demurrage_amount_usd: Optional[float] = None
    despatch_days: Optional[float] = None
    despatch_amount_usd: Optional[float] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
