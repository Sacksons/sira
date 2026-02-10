"""
Pydantic Schemas for API request/response validation
"""

from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserInDB,
    Token, TokenData, TokenPair
)
from app.schemas.movement import MovementCreate, MovementUpdate, MovementResponse
from app.schemas.event import EventCreate, EventResponse
from app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse
from app.schemas.case import CaseCreate, CaseUpdate, CaseResponse
from app.schemas.playbook import PlaybookCreate, PlaybookUpdate, PlaybookResponse
from app.schemas.evidence import EvidenceCreate, EvidenceResponse
from app.schemas.notification import NotificationResponse, NotificationPreferenceUpdate
from app.schemas.vessel import VesselCreate, VesselUpdate, VesselResponse, VesselPositionUpdate
from app.schemas.port import (
    PortCreate, PortUpdate, PortResponse,
    BerthCreate, BerthUpdate, BerthResponse,
    BerthBookingCreate, BerthBookingUpdate, BerthBookingResponse,
)
from app.schemas.asset import (
    AssetCreate, AssetUpdate, AssetResponse,
    DispatchCreate, DispatchUpdate, DispatchResponse,
    MaintenanceCreate, MaintenanceUpdate, MaintenanceResponse,
)
from app.schemas.corridor import (
    CorridorCreate, CorridorUpdate, CorridorResponse,
    GeofenceCreate, GeofenceUpdate, GeofenceResponse,
)
from app.schemas.shipment import (
    ShipmentCreate, ShipmentUpdate, ShipmentResponse, ShipmentDetailResponse,
    MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    CustodyEventCreate, CustodyEventResponse,
    DocumentCreate, DocumentUpdate, DocumentResponse,
    ExceptionCreate, ExceptionUpdate, ExceptionResponse,
)
from app.schemas.freight import (
    FreightRateCreate, FreightRateResponse,
    MarketIndexCreate, MarketIndexResponse,
    DemurrageCreate, DemurrageUpdate, DemurrageResponse,
)
from app.schemas.iot_device import (
    IoTDeviceCreate, IoTDeviceUpdate, IoTDeviceResponse,
    TelemetryCreate, TelemetryResponse,
)

__all__ = [
    "UserCreate", "UserUpdate", "UserResponse", "UserInDB",
    "Token", "TokenData", "TokenPair",
    "MovementCreate", "MovementUpdate", "MovementResponse",
    "EventCreate", "EventResponse",
    "AlertCreate", "AlertUpdate", "AlertResponse",
    "CaseCreate", "CaseUpdate", "CaseResponse",
    "PlaybookCreate", "PlaybookUpdate", "PlaybookResponse",
    "EvidenceCreate", "EvidenceResponse",
    "NotificationResponse", "NotificationPreferenceUpdate",
    "VesselCreate", "VesselUpdate", "VesselResponse", "VesselPositionUpdate",
    "PortCreate", "PortUpdate", "PortResponse",
    "BerthCreate", "BerthUpdate", "BerthResponse",
    "BerthBookingCreate", "BerthBookingUpdate", "BerthBookingResponse",
    "AssetCreate", "AssetUpdate", "AssetResponse",
    "DispatchCreate", "DispatchUpdate", "DispatchResponse",
    "MaintenanceCreate", "MaintenanceUpdate", "MaintenanceResponse",
    "CorridorCreate", "CorridorUpdate", "CorridorResponse",
    "GeofenceCreate", "GeofenceUpdate", "GeofenceResponse",
    "ShipmentCreate", "ShipmentUpdate", "ShipmentResponse", "ShipmentDetailResponse",
    "MilestoneCreate", "MilestoneUpdate", "MilestoneResponse",
    "CustodyEventCreate", "CustodyEventResponse",
    "DocumentCreate", "DocumentUpdate", "DocumentResponse",
    "ExceptionCreate", "ExceptionUpdate", "ExceptionResponse",
    "FreightRateCreate", "FreightRateResponse",
    "MarketIndexCreate", "MarketIndexResponse",
    "DemurrageCreate", "DemurrageUpdate", "DemurrageResponse",
    "IoTDeviceCreate", "IoTDeviceUpdate", "IoTDeviceResponse",
    "TelemetryCreate", "TelemetryResponse",
]
