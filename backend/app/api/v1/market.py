"""
Market Intelligence Routes - Freight rates, market indices, demurrage tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.freight import FreightRate, MarketIndex, DemurrageRecord
from app.models.shipment import Shipment
from app.models.user import User
from app.schemas.freight import (
    FreightRateCreate, FreightRateResponse,
    MarketIndexCreate, MarketIndexResponse,
    DemurrageCreate, DemurrageUpdate, DemurrageResponse,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# --- Freight Rate endpoints ---

@router.get("/rates/", response_model=List[FreightRateResponse])
async def list_freight_rates(
    lane: Optional[str] = None,
    mode: Optional[str] = None,
    corridor_id: Optional[int] = None,
    rate_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List freight rates with optional filtering"""
    query = db.query(FreightRate)
    if lane:
        query = query.filter(FreightRate.lane.ilike(f"%{lane}%"))
    if mode:
        query = query.filter(FreightRate.mode == mode)
    if corridor_id:
        query = query.filter(FreightRate.corridor_id == corridor_id)
    if rate_type:
        query = query.filter(FreightRate.rate_type == rate_type)
    return query.order_by(FreightRate.effective_date.desc()).offset(skip).limit(limit).all()


@router.get("/rates/benchmark")
async def get_rate_benchmarks(
    lane: Optional[str] = None,
    mode: Optional[str] = None,
    days: int = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get freight rate benchmarks (average, min, max) for a lane/mode over a period"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    query = db.query(FreightRate).filter(FreightRate.effective_date >= cutoff)

    if lane:
        query = query.filter(FreightRate.lane.ilike(f"%{lane}%"))
    if mode:
        query = query.filter(FreightRate.mode == mode)

    rates = query.all()
    if not rates:
        return {"message": "No rate data available for this query", "benchmarks": []}

    # Group by lane+mode
    groups = {}
    for r in rates:
        key = f"{r.lane}|{r.mode}"
        if key not in groups:
            groups[key] = {"lane": r.lane, "mode": r.mode, "rates": []}
        groups[key]["rates"].append(r.rate_usd)

    benchmarks = []
    for key, data in groups.items():
        rate_values = data["rates"]
        benchmarks.append({
            "lane": data["lane"],
            "mode": data["mode"],
            "avg_rate": round(sum(rate_values) / len(rate_values), 2),
            "min_rate": min(rate_values),
            "max_rate": max(rate_values),
            "sample_count": len(rate_values),
            "period_days": days,
        })

    return {"benchmarks": benchmarks}


@router.post("/rates/", response_model=FreightRateResponse, status_code=status.HTTP_201_CREATED)
async def create_freight_rate(
    data: FreightRateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Add a new freight rate data point"""
    rate = FreightRate(**data.model_dump())
    db.add(rate)
    db.commit()
    db.refresh(rate)
    logger.info(f"Freight rate added: {rate.lane} {rate.mode} ${rate.rate_usd} by {current_user.username}")
    return rate


# --- Market Index endpoints ---

@router.get("/indices/", response_model=List[MarketIndexResponse])
async def list_market_indices(
    index_name: Optional[str] = None,
    index_type: Optional[str] = None,
    days: int = 30,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List market indices"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    query = db.query(MarketIndex).filter(MarketIndex.recorded_at >= cutoff)
    if index_name:
        query = query.filter(MarketIndex.index_name.ilike(f"%{index_name}%"))
    if index_type:
        query = query.filter(MarketIndex.index_type == index_type)
    return query.order_by(MarketIndex.recorded_at.desc()).offset(skip).limit(limit).all()


@router.get("/indices/latest")
async def get_latest_indices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the latest value for each market index"""
    subq = db.query(
        MarketIndex.index_name,
        func.max(MarketIndex.recorded_at).label("max_date")
    ).group_by(MarketIndex.index_name).subquery()

    latest = db.query(MarketIndex).join(
        subq,
        (MarketIndex.index_name == subq.c.index_name) &
        (MarketIndex.recorded_at == subq.c.max_date)
    ).all()

    return [{
        "index_name": idx.index_name,
        "index_type": idx.index_type,
        "value": idx.value,
        "unit": idx.unit,
        "change_pct": idx.change_pct,
        "recorded_at": idx.recorded_at.isoformat() if idx.recorded_at else None,
    } for idx in latest]


@router.post("/indices/", response_model=MarketIndexResponse, status_code=status.HTTP_201_CREATED)
async def create_market_index(
    data: MarketIndexCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Add a new market index data point"""
    index = MarketIndex(**data.model_dump())
    db.add(index)
    db.commit()
    db.refresh(index)
    return index


# --- Demurrage endpoints ---

@router.get("/demurrage/", response_model=List[DemurrageResponse])
async def list_demurrage_records(
    shipment_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List demurrage records"""
    query = db.query(DemurrageRecord)
    if shipment_id:
        query = query.filter(DemurrageRecord.shipment_id == shipment_id)
    if status_filter:
        query = query.filter(DemurrageRecord.status == status_filter)
    return query.order_by(DemurrageRecord.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/demurrage/exposure")
async def get_demurrage_exposure(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get total demurrage exposure across all active shipments"""
    active_shipments = db.query(Shipment).filter(
        Shipment.status.notin_(["completed", "cancelled"])
    ).all()

    total_exposure = sum(s.demurrage_exposure_usd or 0 for s in active_shipments)
    total_demurrage_days = sum(s.demurrage_days or 0 for s in active_shipments)
    high_risk_count = sum(1 for s in active_shipments if (s.demurrage_risk_score or 0) >= 70)

    return {
        "total_exposure_usd": round(total_exposure, 2),
        "total_demurrage_days": round(total_demurrage_days, 1),
        "active_shipments": len(active_shipments),
        "high_risk_shipments": high_risk_count,
        "avg_risk_score": round(
            sum(s.demurrage_risk_score or 0 for s in active_shipments) / max(len(active_shipments), 1), 1
        ),
    }


@router.post("/demurrage/", response_model=DemurrageResponse, status_code=status.HTTP_201_CREATED)
async def create_demurrage_record(
    data: DemurrageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Create a demurrage tracking record"""
    record = DemurrageRecord(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/demurrage/{record_id}", response_model=DemurrageResponse)
async def update_demurrage_record(
    record_id: int,
    data: DemurrageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "supervisor", "admin"]))
):
    """Update demurrage calculation"""
    record = db.query(DemurrageRecord).filter(DemurrageRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demurrage record not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)

    # Auto-calculate demurrage amount if days and rate are set
    if record.demurrage_days and record.demurrage_rate_usd:
        record.demurrage_amount_usd = round(record.demurrage_days * record.demurrage_rate_usd, 2)

    db.commit()
    db.refresh(record)
    return record
