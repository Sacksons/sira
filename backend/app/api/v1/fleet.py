"""
Fleet & Asset Routes - Asset management, dispatch, and maintenance
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.asset import Asset, MaintenanceRecord, DispatchRecord
from app.models.user import User
from app.schemas.asset import (
    AssetCreate, AssetUpdate, AssetResponse,
    DispatchCreate, DispatchUpdate, DispatchResponse,
    MaintenanceCreate, MaintenanceUpdate, MaintenanceResponse,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# --- Asset endpoints ---

@router.get("/assets/", response_model=List[AssetResponse])
async def list_assets(
    skip: int = 0,
    limit: int = 100,
    asset_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    corridor_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all fleet assets with optional filtering"""
    query = db.query(Asset)
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    if status_filter:
        query = query.filter(Asset.status == status_filter)
    if corridor_id:
        query = query.filter(Asset.assigned_corridor_id == corridor_id)
    return query.order_by(Asset.asset_code).offset(skip).limit(limit).all()


@router.get("/assets/availability")
async def get_asset_availability(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get asset availability board summary"""
    results = db.query(
        Asset.asset_type,
        Asset.status,
        func.count(Asset.id)
    ).group_by(Asset.asset_type, Asset.status).all()

    availability = {}
    for asset_type, asset_status, count in results:
        if asset_type not in availability:
            availability[asset_type] = {"total": 0, "statuses": {}}
        availability[asset_type]["statuses"][asset_status] = count
        availability[asset_type]["total"] += count

    return availability


@router.get("/assets/utilization")
async def get_fleet_utilization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get fleet utilization analytics"""
    assets = db.query(Asset).all()
    if not assets:
        return {"avg_utilization": 0, "by_type": {}}

    by_type = {}
    total_util = 0
    for asset in assets:
        t = asset.asset_type
        if t not in by_type:
            by_type[t] = {"count": 0, "total_utilization": 0, "in_transit": 0, "idle": 0}
        by_type[t]["count"] += 1
        by_type[t]["total_utilization"] += asset.utilization_pct or 0
        if asset.status == "in_transit":
            by_type[t]["in_transit"] += 1
        if asset.status in ("idle", "available"):
            by_type[t]["idle"] += 1
        total_util += asset.utilization_pct or 0

    for t in by_type:
        by_type[t]["avg_utilization"] = round(by_type[t]["total_utilization"] / by_type[t]["count"], 1)
        del by_type[t]["total_utilization"]

    return {
        "total_assets": len(assets),
        "avg_utilization": round(total_util / len(assets), 1),
        "by_type": by_type,
    }


@router.get("/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get asset by ID"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return asset


@router.post("/assets/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    data: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["supervisor", "admin"]))
):
    """Create a new fleet asset"""
    existing = db.query(Asset).filter(Asset.asset_code == data.asset_code).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Asset with this code already exists")

    asset = Asset(**data.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    logger.info(f"Asset created: {asset.asset_code} by {current_user.username}")
    return asset


@router.put("/assets/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    data: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Update asset details"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(asset, field, value)
    db.commit()
    db.refresh(asset)
    return asset


# --- Dispatch endpoints ---

@router.get("/dispatch/", response_model=List[DispatchResponse])
async def list_dispatches(
    asset_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List dispatch records"""
    query = db.query(DispatchRecord)
    if asset_id:
        query = query.filter(DispatchRecord.asset_id == asset_id)
    if status_filter:
        query = query.filter(DispatchRecord.status == status_filter)
    return query.order_by(DispatchRecord.dispatched_at.desc()).offset(skip).limit(limit).all()


@router.post("/dispatch/", response_model=DispatchResponse, status_code=status.HTTP_201_CREATED)
async def create_dispatch(
    data: DispatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Create a new dispatch record"""
    asset = db.query(Asset).filter(Asset.id == data.asset_id).first()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    dispatch = DispatchRecord(**data.model_dump())
    db.add(dispatch)

    asset.status = "in_transit"
    asset.assigned_shipment_id = data.shipment_id

    db.commit()
    db.refresh(dispatch)
    logger.info(f"Dispatch created for asset {data.asset_id} by {current_user.username}")
    return dispatch


@router.put("/dispatch/{dispatch_id}", response_model=DispatchResponse)
async def update_dispatch(
    dispatch_id: int,
    data: DispatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Update dispatch status"""
    dispatch = db.query(DispatchRecord).filter(DispatchRecord.id == dispatch_id).first()
    if not dispatch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispatch not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(dispatch, field, value)

    if data.status == "completed":
        asset = db.query(Asset).filter(Asset.id == dispatch.asset_id).first()
        if asset:
            asset.status = "available"
            asset.assigned_shipment_id = None
            asset.total_trips = (asset.total_trips or 0) + 1

    db.commit()
    db.refresh(dispatch)
    return dispatch


# --- Maintenance endpoints ---

@router.get("/maintenance/", response_model=List[MaintenanceResponse])
async def list_maintenance(
    asset_id: Optional[int] = None,
    vessel_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List maintenance records"""
    query = db.query(MaintenanceRecord)
    if asset_id:
        query = query.filter(MaintenanceRecord.asset_id == asset_id)
    if vessel_id:
        query = query.filter(MaintenanceRecord.vessel_id == vessel_id)
    if status_filter:
        query = query.filter(MaintenanceRecord.status == status_filter)
    return query.order_by(MaintenanceRecord.scheduled_date.desc()).offset(skip).limit(limit).all()


@router.post("/maintenance/", response_model=MaintenanceResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance(
    data: MaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Schedule a maintenance record"""
    record = MaintenanceRecord(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info(f"Maintenance scheduled: {record.maintenance_type} by {current_user.username}")
    return record


@router.put("/maintenance/{record_id}", response_model=MaintenanceResponse)
async def update_maintenance(
    record_id: int,
    data: MaintenanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Update maintenance record"""
    record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance record not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record
