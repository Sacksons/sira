"""
Shipment Routes - End-to-end shipment tracking, milestones, documents, custody, and exceptions
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import hashlib
import json

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.shipment import (
    Shipment, ShipmentMilestone, CustodyEvent,
    ShipmentDocument, ShipmentException,
)
from app.models.user import User
from app.schemas.shipment import (
    ShipmentCreate, ShipmentUpdate, ShipmentResponse, ShipmentDetailResponse,
    MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    CustodyEventCreate, CustodyEventResponse,
    DocumentCreate, DocumentUpdate, DocumentResponse,
    ExceptionCreate, ExceptionUpdate, ExceptionResponse,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# --- Shipment endpoints ---

@router.get("/", response_model=List[ShipmentResponse])
async def list_shipments(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    corridor_id: Optional[int] = None,
    vessel_id: Optional[int] = None,
    cargo_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all shipments with optional filtering"""
    query = db.query(Shipment)
    if status_filter:
        query = query.filter(Shipment.status == status_filter)
    if corridor_id:
        query = query.filter(Shipment.corridor_id == corridor_id)
    if vessel_id:
        query = query.filter(Shipment.vessel_id == vessel_id)
    if cargo_type:
        query = query.filter(Shipment.cargo_type == cargo_type)
    return query.order_by(Shipment.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/active", response_model=List[ShipmentResponse])
async def list_active_shipments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all active (non-completed, non-cancelled) shipments for control tower"""
    return db.query(Shipment).filter(
        Shipment.status.notin_(["completed", "cancelled"])
    ).order_by(Shipment.demurrage_risk_score.desc()).all()


@router.get("/at-risk")
async def list_at_risk_shipments(
    threshold: float = 50.0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List shipments with high demurrage risk"""
    shipments = db.query(Shipment).filter(
        Shipment.demurrage_risk_score >= threshold,
        Shipment.status.notin_(["completed", "cancelled"])
    ).order_by(Shipment.demurrage_risk_score.desc()).all()

    return [{
        "id": s.id,
        "shipment_ref": s.shipment_ref,
        "cargo_type": s.cargo_type,
        "origin": s.origin,
        "destination": s.destination,
        "status": s.status,
        "demurrage_risk_score": s.demurrage_risk_score,
        "demurrage_exposure_usd": s.demurrage_exposure_usd,
        "eta_destination": s.eta_destination.isoformat() if s.eta_destination else None,
        "eta_confidence": s.eta_confidence,
    } for s in shipments]


@router.get("/{shipment_id}", response_model=ShipmentDetailResponse)
async def get_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get shipment with full details including milestones, custody events, documents, and exceptions"""
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found")
    return shipment


@router.post("/", response_model=ShipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_shipment(
    data: ShipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Create a new shipment"""
    if data.laycan_start >= data.laycan_end:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="laycan_start must be before laycan_end")

    existing = db.query(Shipment).filter(Shipment.shipment_ref == data.shipment_ref).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Shipment ref already exists")

    shipment = Shipment(**data.model_dump())
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    logger.info(f"Shipment created: {shipment.shipment_ref} by {current_user.username}")
    return shipment


@router.put("/{shipment_id}", response_model=ShipmentResponse)
async def update_shipment(
    shipment_id: int,
    data: ShipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Update shipment details"""
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(shipment, field, value)

    if data.eta_destination:
        shipment.eta_updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(shipment)
    return shipment


# --- Milestone endpoints ---

@router.get("/{shipment_id}/milestones", response_model=List[MilestoneResponse])
async def list_milestones(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List milestones for a shipment"""
    return db.query(ShipmentMilestone).filter(
        ShipmentMilestone.shipment_id == shipment_id
    ).order_by(ShipmentMilestone.planned_time).all()


@router.post("/{shipment_id}/milestones", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
async def create_milestone(
    shipment_id: int,
    data: MilestoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Add a milestone to a shipment"""
    milestone = ShipmentMilestone(**data.model_dump())
    milestone.shipment_id = shipment_id
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


@router.put("/milestones/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    milestone_id: int,
    data: MilestoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Update a milestone (e.g., mark as completed with actual time)"""
    milestone = db.query(ShipmentMilestone).filter(ShipmentMilestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

    if data.actual_time and milestone.planned_time:
        milestone.variance_hours = (data.actual_time - milestone.planned_time).total_seconds() / 3600

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(milestone, field, value)

    db.commit()
    db.refresh(milestone)
    return milestone


# --- Custody Event endpoints ---

@router.get("/{shipment_id}/custody", response_model=List[CustodyEventResponse])
async def list_custody_events(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List chain-of-custody events for a shipment"""
    return db.query(CustodyEvent).filter(
        CustodyEvent.shipment_id == shipment_id
    ).order_by(CustodyEvent.timestamp).all()


@router.post("/{shipment_id}/custody", response_model=CustodyEventResponse, status_code=status.HTTP_201_CREATED)
async def create_custody_event(
    shipment_id: int,
    data: CustodyEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Record a chain-of-custody event"""
    event = CustodyEvent(**data.model_dump())
    event.shipment_id = shipment_id
    event.created_by = current_user.id

    # Calculate volume variance if both volumes provided
    if data.measured_volume and data.expected_volume and data.expected_volume > 0:
        event.volume_variance_pct = round(
            ((data.measured_volume - data.expected_volume) / data.expected_volume) * 100, 2
        )

    # Generate digital signature (hash of event data)
    sig_data = json.dumps({
        "shipment_id": shipment_id,
        "event_type": data.event_type,
        "timestamp": event.timestamp.isoformat() if event.timestamp else None,
        "seal_number": data.seal_number,
        "measured_volume": data.measured_volume,
        "from_party": data.from_party,
        "to_party": data.to_party,
    }, sort_keys=True)
    event.digital_signature = hashlib.sha256(sig_data.encode()).hexdigest()

    db.add(event)
    db.commit()
    db.refresh(event)
    logger.info(f"Custody event recorded for shipment {shipment_id} by {current_user.username}")
    return event


# --- Document endpoints ---

@router.get("/{shipment_id}/documents", response_model=List[DocumentResponse])
async def list_documents(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List documents for a shipment"""
    return db.query(ShipmentDocument).filter(
        ShipmentDocument.shipment_id == shipment_id
    ).order_by(ShipmentDocument.created_at.desc()).all()


@router.post("/{shipment_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    shipment_id: int,
    data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Add a document to a shipment"""
    doc = ShipmentDocument(**data.model_dump())
    doc.shipment_id = shipment_id
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.put("/documents/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: int,
    data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Update document status (verify/reject)"""
    doc = db.query(ShipmentDocument).filter(ShipmentDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if data.status == "verified":
        doc.verified_by = current_user.id
        doc.verified_at = datetime.now(timezone.utc)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(doc, field, value)
    db.commit()
    db.refresh(doc)
    return doc


# --- Exception endpoints ---

@router.get("/{shipment_id}/exceptions", response_model=List[ExceptionResponse])
async def list_exceptions(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List exceptions for a shipment"""
    return db.query(ShipmentException).filter(
        ShipmentException.shipment_id == shipment_id
    ).order_by(ShipmentException.created_at.desc()).all()


@router.post("/{shipment_id}/exceptions", response_model=ExceptionResponse, status_code=status.HTTP_201_CREATED)
async def create_exception(
    shipment_id: int,
    data: ExceptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Report an exception for a shipment"""
    exc = ShipmentException(**data.model_dump())
    exc.shipment_id = shipment_id
    db.add(exc)
    db.commit()
    db.refresh(exc)
    logger.info(f"Exception reported for shipment {shipment_id}: {data.exception_type} by {current_user.username}")
    return exc


@router.put("/exceptions/{exc_id}", response_model=ExceptionResponse)
async def update_exception(
    exc_id: int,
    data: ExceptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Update exception status"""
    exc = db.query(ShipmentException).filter(ShipmentException.id == exc_id).first()
    if not exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exception not found")

    if data.status == "resolved":
        exc.resolved_at = datetime.now(timezone.utc)
        exc.resolved_by = current_user.id

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(exc, field, value)
    db.commit()
    db.refresh(exc)
    return exc
