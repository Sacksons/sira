"""
Corridor Routes - Mining/energy corridor management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.corridor import Corridor, Geofence
from app.models.user import User
from app.schemas.corridor import (
    CorridorCreate, CorridorUpdate, CorridorResponse,
    GeofenceCreate, GeofenceUpdate, GeofenceResponse,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[CorridorResponse])
async def list_corridors(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    country: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all corridors"""
    query = db.query(Corridor)
    if status_filter:
        query = query.filter(Corridor.status == status_filter)
    if country:
        query = query.filter(Corridor.country == country)
    return query.order_by(Corridor.name).offset(skip).limit(limit).all()


@router.get("/{corridor_id}", response_model=CorridorResponse)
async def get_corridor(
    corridor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get corridor by ID"""
    corridor = db.query(Corridor).filter(Corridor.id == corridor_id).first()
    if not corridor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Corridor not found")
    return corridor


@router.post("/", response_model=CorridorResponse, status_code=status.HTTP_201_CREATED)
async def create_corridor(
    data: CorridorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["supervisor", "admin"]))
):
    """Create a new corridor"""
    existing = db.query(Corridor).filter(Corridor.code == data.code).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Corridor with this code already exists")

    corridor = Corridor(**data.model_dump())
    db.add(corridor)
    db.commit()
    db.refresh(corridor)
    logger.info(f"Corridor created: {corridor.name} ({corridor.code}) by {current_user.username}")
    return corridor


@router.put("/{corridor_id}", response_model=CorridorResponse)
async def update_corridor(
    corridor_id: int,
    data: CorridorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Update corridor details"""
    corridor = db.query(Corridor).filter(Corridor.id == corridor_id).first()
    if not corridor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Corridor not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(corridor, field, value)
    db.commit()
    db.refresh(corridor)
    return corridor


# --- Geofence endpoints ---

@router.get("/{corridor_id}/geofences", response_model=List[GeofenceResponse])
async def list_geofences(
    corridor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List geofences for a corridor"""
    return db.query(Geofence).filter(Geofence.corridor_id == corridor_id).all()


@router.post("/geofences/", response_model=GeofenceResponse, status_code=status.HTTP_201_CREATED)
async def create_geofence(
    data: GeofenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["supervisor", "admin"]))
):
    """Create a new geofence"""
    geofence = Geofence(**data.model_dump())
    db.add(geofence)
    db.commit()
    db.refresh(geofence)
    return geofence


@router.put("/geofences/{geofence_id}", response_model=GeofenceResponse)
async def update_geofence(
    geofence_id: int,
    data: GeofenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["supervisor", "admin"]))
):
    """Update a geofence"""
    geofence = db.query(Geofence).filter(Geofence.id == geofence_id).first()
    if not geofence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Geofence not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(geofence, field, value)
    db.commit()
    db.refresh(geofence)
    return geofence
