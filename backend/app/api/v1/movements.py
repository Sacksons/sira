"""
Movement Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.movement import Movement
from app.models.user import User
from app.schemas.movement import MovementCreate, MovementUpdate, MovementResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[MovementResponse])
async def list_movements(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all movements with optional filtering"""
    query = db.query(Movement)

    if status:
        query = query.filter(Movement.status == status)

    movements = query.order_by(Movement.created_at.desc()).offset(skip).limit(limit).all()
    return movements


@router.get("/{movement_id}", response_model=MovementResponse)
async def get_movement(
    movement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get movement by ID"""
    movement = db.query(Movement).filter(Movement.id == movement_id).first()
    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movement not found"
        )
    return movement


@router.post("/", response_model=MovementResponse, status_code=status.HTTP_201_CREATED)
async def create_movement(
    movement_data: MovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Create a new movement"""
    if movement_data.laycan_start >= movement_data.laycan_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="laycan_start must be before laycan_end"
        )

    movement = Movement(**movement_data.model_dump())
    db.add(movement)
    db.commit()
    db.refresh(movement)

    logger.info(f"Movement created: ID {movement.id} by {current_user.username}")
    return movement


@router.put("/{movement_id}", response_model=MovementResponse)
async def update_movement(
    movement_id: int,
    movement_data: MovementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Update a movement"""
    movement = db.query(Movement).filter(Movement.id == movement_id).first()
    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movement not found"
        )

    update_data = movement_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(movement, field, value)

    db.commit()
    db.refresh(movement)

    logger.info(f"Movement updated: ID {movement.id} by {current_user.username}")
    return movement


@router.delete("/{movement_id}")
async def delete_movement(
    movement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["supervisor", "admin"]))
):
    """Delete a movement"""
    movement = db.query(Movement).filter(Movement.id == movement_id).first()
    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movement not found"
        )

    db.delete(movement)
    db.commit()

    logger.info(f"Movement deleted: ID {movement_id} by {current_user.username}")
    return {"message": "Movement deleted successfully"}


@router.put("/{movement_id}/location")
async def update_movement_location(
    movement_id: int,
    location: str,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Update movement's current location"""
    movement = db.query(Movement).filter(Movement.id == movement_id).first()
    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movement not found"
        )

    movement.current_location = location
    if lat is not None:
        movement.current_lat = lat
    if lng is not None:
        movement.current_lng = lng

    db.commit()

    logger.info(f"Movement location updated: ID {movement_id} to {location}")
    return {"message": "Location updated successfully", "location": location}
