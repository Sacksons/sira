"""
Freight Rate & Market Intelligence Model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class FreightRate(Base):
    __tablename__ = "freight_rates"

    id = Column(Integer, primary_key=True, index=True)
    corridor_id = Column(Integer, ForeignKey("corridors.id"), nullable=True)
    lane = Column(String(255), nullable=False, index=True)  # e.g., "Conakry-Rotterdam"
    mode = Column(String(50), nullable=False, index=True)  # truck, rail, barge, vessel
    cargo_type = Column(String(100))

    # Rate data
    rate_usd = Column(Float, nullable=False)  # per tonne or per TEU or per day
    rate_unit = Column(String(50), nullable=False)  # per_tonne, per_teu, per_day
    currency = Column(String(10), default="USD")
    rate_type = Column(String(50))  # spot, contract, benchmark
    source = Column(String(255))  # data source

    # Validity
    effective_date = Column(DateTime(timezone=True), nullable=False)
    expiry_date = Column(DateTime(timezone=True))

    # Vessel-specific (for ocean freight)
    vessel_class = Column(String(100))  # capesize, panamax, supramax, handymax
    vessel_size_dwt_min = Column(Float)
    vessel_size_dwt_max = Column(Float)

    # Market context
    fuel_surcharge = Column(Float)
    port_charges = Column(Float)
    total_cost = Column(Float)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    corridor = relationship("Corridor", back_populates="freight_rates")

    def __repr__(self):
        return f"<FreightRate(id={self.id}, lane='{self.lane}', rate={self.rate_usd})>"


class MarketIndex(Base):
    __tablename__ = "market_indices"

    id = Column(Integer, primary_key=True, index=True)
    index_name = Column(String(255), nullable=False, index=True)  # e.g., "BDI", "Capesize_TCE", "WestAfrica_Iron_Ore"
    index_type = Column(String(100))  # freight, commodity, port_congestion
    value = Column(Float, nullable=False)
    unit = Column(String(50))
    change_pct = Column(Float)  # daily change %
    change_abs = Column(Float)  # absolute change
    period = Column(String(50))  # daily, weekly, monthly
    source = Column(String(255))
    recorded_at = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<MarketIndex(name='{self.index_name}', value={self.value})>"


class DemurrageRecord(Base):
    __tablename__ = "demurrage_records"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    vessel_id = Column(Integer, ForeignKey("vessels.id"), nullable=True)
    port_id = Column(Integer, ForeignKey("ports.id"), nullable=True)

    # Demurrage calculation
    laycan_start = Column(DateTime(timezone=True))
    laycan_end = Column(DateTime(timezone=True))
    nor_tendered = Column(DateTime(timezone=True))  # Notice of Readiness
    laytime_start = Column(DateTime(timezone=True))
    laytime_end = Column(DateTime(timezone=True))
    laytime_allowed_hours = Column(Float)
    laytime_used_hours = Column(Float)
    demurrage_start = Column(DateTime(timezone=True))
    demurrage_end = Column(DateTime(timezone=True))
    demurrage_days = Column(Float)
    demurrage_rate_usd = Column(Float)  # per day
    demurrage_amount_usd = Column(Float)
    despatch_days = Column(Float)  # if discharged early
    despatch_amount_usd = Column(Float)

    # Status
    status = Column(String(50), default="accruing")  # accruing, calculated, disputed, settled
    notes = Column(Text)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<DemurrageRecord(id={self.id}, days={self.demurrage_days}, amount=${self.demurrage_amount_usd})>"
