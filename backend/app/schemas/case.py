"""
Case Schemas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class CaseBase(BaseModel):
    """Base case schema"""
    title: str = Field(..., min_length=1, max_length=255)
    overview: Optional[str] = None
    priority: str = Field(
        default="medium",
        pattern="^(low|medium|high|critical)$"
    )
    category: Optional[str] = Field(None, max_length=100)


class CaseCreate(CaseBase):
    """Schema for creating a case"""
    alert_ids: Optional[List[int]] = None  # Link alerts to case


class CaseUpdate(BaseModel):
    """Schema for updating a case"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    overview: Optional[str] = None
    priority: Optional[str] = Field(
        None,
        pattern="^(low|medium|high|critical)$"
    )
    category: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(
        None,
        pattern="^(open|investigating|pending|closed)$"
    )
    assigned_to: Optional[int] = None
    costs: Optional[float] = Field(None, ge=0)
    parties: Optional[str] = None
    timeline: Optional[str] = None
    actions: Optional[str] = None


class CaseResponse(CaseBase):
    """Schema for case response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_number: Optional[str] = None
    status: str
    costs: float
    assigned_to: Optional[int] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None


class CaseClose(BaseModel):
    """Schema for closing a case"""
    closure_code: str = Field(..., min_length=1, max_length=100)
    resolution_summary: Optional[str] = None
    final_costs: Optional[float] = Field(None, ge=0)


class CaseExport(BaseModel):
    """Schema for case export response"""
    case: CaseResponse
    alerts_count: int
    evidences_count: int
    export_timestamp: datetime
    format: str = "JSON"
