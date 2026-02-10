"""
Port & Terminal Routes - Port operations, berth management, and bookings
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.port import Port, Berth, BerthBooking
from app.models.user import User
from app.schemas.port import (
    PortCreate, PortUpdate, PortResponse,
    BerthCreate, BerthUpdate, BerthResponse,
    BerthBookingCreate, BerthBookingUpdate, BerthBookingResponse,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# --- Port endpoints ---

@router.get("/", response_model=List[PortResponse])
async def list_ports(
    skip: int = 0,
    limit: int = 100,
    country: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all ports"""
    query = db.query(Port)
    if country:
        query = query.filter(Port.country == country)
    if status_filter:
        query = query.filter(Port.status == status_filter)
    return query.order_by(Port.name).offset(skip).limit(limit).all()


@router.get("/{port_id}", response_model=PortResponse)
async def get_port(
    port_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get port by ID"""
    port = db.query(Port).filter(Port.id == port_id).first()
    if not port:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Port not found")
    return port


@router.post("/", response_model=PortResponse, status_code=status.HTTP_201_CREATED)
async def create_port(
    data: PortCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["supervisor", "admin"]))
):
    """Create a new port"""
    existing = db.query(Port).filter(Port.code == data.code).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Port with this code already exists")

    port = Port(**data.model_dump())
    db.add(port)
    db.commit()
    db.refresh(port)
    logger.info(f"Port created: {port.name} ({port.code}) by {current_user.username}")
    return port


@router.put("/{port_id}", response_model=PortResponse)
async def update_port(
    port_id: int,
    data: PortUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Update port details"""
    port = db.query(Port).filter(Port.id == port_id).first()
    if not port:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Port not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(port, field, value)
    db.commit()
    db.refresh(port)
    return port


# --- Berth endpoints ---

@router.get("/{port_id}/berths", response_model=List[BerthResponse])
async def list_berths(
    port_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List berths for a port"""
    return db.query(Berth).filter(Berth.port_id == port_id).order_by(Berth.name).all()


@router.post("/{port_id}/berths", response_model=BerthResponse, status_code=status.HTTP_201_CREATED)
async def create_berth(
    port_id: int,
    data: BerthCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["supervisor", "admin"]))
):
    """Create a berth at a port"""
    port = db.query(Port).filter(Port.id == port_id).first()
    if not port:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Port not found")

    berth = Berth(**data.model_dump())
    berth.port_id = port_id
    db.add(berth)
    db.commit()
    db.refresh(berth)
    return berth


@router.put("/berths/{berth_id}", response_model=BerthResponse)
async def update_berth(
    berth_id: int,
    data: BerthUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Update berth details"""
    berth = db.query(Berth).filter(Berth.id == berth_id).first()
    if not berth:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Berth not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(berth, field, value)
    db.commit()
    db.refresh(berth)
    return berth


# --- Berth Booking endpoints ---

@router.get("/bookings/", response_model=List[BerthBookingResponse])
async def list_berth_bookings(
    berth_id: Optional[int] = None,
    vessel_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List berth bookings with optional filtering"""
    query = db.query(BerthBooking)
    if berth_id:
        query = query.filter(BerthBooking.berth_id == berth_id)
    if vessel_id:
        query = query.filter(BerthBooking.vessel_id == vessel_id)
    if status_filter:
        query = query.filter(BerthBooking.status == status_filter)
    return query.order_by(BerthBooking.scheduled_arrival).offset(skip).limit(limit).all()


@router.post("/bookings/", response_model=BerthBookingResponse, status_code=status.HTTP_201_CREATED)
async def create_berth_booking(
    data: BerthBookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Create a berth booking"""
    if data.scheduled_arrival >= data.scheduled_departure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arrival must be before departure")

    booking = BerthBooking(**data.model_dump())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    logger.info(f"Berth booking created: berth {data.berth_id}, vessel {data.vessel_id} by {current_user.username}")
    return booking


@router.put("/bookings/{booking_id}", response_model=BerthBookingResponse)
async def update_berth_booking(
    booking_id: int,
    data: BerthBookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Update a berth booking"""
    booking = db.query(BerthBooking).filter(BerthBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(booking, field, value)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/congestion/summary")
async def get_port_congestion_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get port congestion summary for all ports"""
    ports = db.query(Port).filter(Port.status != "closed").all()
    summary = []
    for port in ports:
        active_bookings = db.query(BerthBooking).join(Berth).filter(
            Berth.port_id == port.id,
            BerthBooking.status.in_(["scheduled", "confirmed", "active"])
        ).count()

        total_berths = db.query(Berth).filter(Berth.port_id == port.id).count()
        available_berths = db.query(Berth).filter(
            Berth.port_id == port.id,
            Berth.status == "available"
        ).count()

        summary.append({
            "port_id": port.id,
            "port_name": port.name,
            "port_code": port.code,
            "status": port.status,
            "current_queue": port.current_queue,
            "avg_wait_days": port.avg_wait_days,
            "avg_dwell_days": port.avg_dwell_days,
            "total_berths": total_berths,
            "available_berths": available_berths,
            "active_bookings": active_bookings,
            "utilization_pct": round((1 - available_berths / max(total_berths, 1)) * 100, 1),
        })
    return summary
