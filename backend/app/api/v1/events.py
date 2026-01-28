"""
Event Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.event import Event
from app.models.movement import Movement
from app.models.user import User
from app.schemas.event import EventCreate, EventResponse
from app.services.alert_engine import AlertDerivationEngine
from app.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


async def process_event_alerts(event_id: int, db_url: str):
    """Background task to process alerts for an event"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if event:
            alert_engine = AlertDerivationEngine(db)
            created_alerts = alert_engine.process_event(event)

            if created_alerts:
                notification_service = NotificationService(db)
                for alert in created_alerts:
                    await notification_service.notify_alert({
                        "id": alert.id,
                        "severity": alert.severity,
                        "description": alert.description,
                        "domain": alert.domain,
                        "created_at": alert.created_at.isoformat() if alert.created_at else None
                    })
    except Exception as e:
        logger.error(f"Error processing event alerts: {e}")
    finally:
        db.close()


@router.get("/", response_model=List[EventResponse])
async def list_events(
    movement_id: Optional[int] = None,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List events with optional filtering"""
    query = db.query(Event)

    if movement_id:
        query = query.filter(Event.movement_id == movement_id)
    if event_type:
        query = query.filter(Event.event_type == event_type)
    if severity:
        query = query.filter(Event.severity == severity)

    events = query.order_by(Event.timestamp.desc()).offset(skip).limit(limit).all()
    return events


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get event by ID"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new event.
    Security events will automatically trigger the alert derivation engine.
    """
    # Verify movement exists
    movement = db.query(Movement).filter(Movement.id == event_data.movement_id).first()
    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movement not found"
        )

    event = Event(**event_data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)

    logger.info(f"Event created: ID {event.id} for Movement {event_data.movement_id}")

    # Process alerts in background for security events
    if event_data.event_type == "security" or event_data.severity == "critical":
        # Process synchronously for immediate alert generation
        alert_engine = AlertDerivationEngine(db)
        created_alerts = alert_engine.process_event(event)
        if created_alerts:
            logger.info(f"Created {len(created_alerts)} alerts from event {event.id}")

    return event


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    db.delete(event)
    db.commit()

    logger.info(f"Event deleted: ID {event_id}")
    return {"message": "Event deleted successfully"}
