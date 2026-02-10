"""
Vessel Routes - Vessel tracking and management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.vessel import Vessel
from app.models.user import User
from app.schemas.vessel import VesselCreate, VesselUpdate, VesselResponse, VesselPositionUpdate
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[VesselResponse])
async def list_vessels(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    vessel_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all vessels with optional filtering"""
    query = db.query(Vessel)
    if status:
        query = query.filter(Vessel.status == status)
    if vessel_type:
        query = query.filter(Vessel.vessel_type == vessel_type)
    return query.order_by(Vessel.name).offset(skip).limit(limit).all()


@router.get("/positions", response_model=List[VesselResponse])
async def get_vessel_positions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current positions of all active vessels (for map view)"""
    vessels = db.query(Vessel).filter(
        Vessel.status.in_(["active", "idle"]),
        Vessel.current_lat.isnot(None),
        Vessel.current_lng.isnot(None)
    ).all()
    return vessels


@router.get("/{vessel_id}", response_model=VesselResponse)
async def get_vessel(
    vessel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get vessel by ID"""
    vessel = db.query(Vessel).filter(Vessel.id == vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vessel not found")
    return vessel


@router.post("/", response_model=VesselResponse, status_code=status.HTTP_201_CREATED)
async def create_vessel(
    data: VesselCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Create a new vessel"""
    existing = db.query(Vessel).filter(Vessel.imo_number == data.imo_number).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Vessel with this IMO number already exists")

    vessel = Vessel(**data.model_dump())
    db.add(vessel)
    db.commit()
    db.refresh(vessel)
    logger.info(f"Vessel created: {vessel.name} (IMO: {vessel.imo_number}) by {current_user.username}")
    return vessel


@router.put("/{vessel_id}", response_model=VesselResponse)
async def update_vessel(
    vessel_id: int,
    data: VesselUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Update vessel details"""
    vessel = db.query(Vessel).filter(Vessel.id == vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vessel not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(vessel, field, value)
    db.commit()
    db.refresh(vessel)
    logger.info(f"Vessel updated: ID {vessel_id} by {current_user.username}")
    return vessel


@router.put("/{vessel_id}/position", response_model=VesselResponse)
async def update_vessel_position(
    vessel_id: int,
    data: VesselPositionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Update vessel's current position (AIS data ingestion)"""
    vessel = db.query(Vessel).filter(Vessel.id == vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vessel not found")

    vessel.current_lat = data.latitude
    vessel.current_lng = data.longitude
    vessel.current_speed = data.speed
    vessel.current_heading = data.heading
    vessel.current_destination = data.destination
    vessel.ais_status = data.ais_status
    vessel.position_updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(vessel)
    return vessel


@router.delete("/{vessel_id}")
async def delete_vessel(
    vessel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["supervisor", "admin"]))
):
    """Delete a vessel"""
    vessel = db.query(Vessel).filter(Vessel.id == vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vessel not found")

    db.delete(vessel)
    db.commit()
    logger.info(f"Vessel deleted: ID {vessel_id} by {current_user.username}")
    return {"message": "Vessel deleted successfully"}
