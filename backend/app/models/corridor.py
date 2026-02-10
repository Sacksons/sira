"""
Corridor Model - Mining/energy logistics corridors
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class Corridor(Base):
    __tablename__ = "corridors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, index=True)
    corridor_type = Column(String(100))  # mining, oil_gas, multi_commodity
    country = Column(String(100))
    region = Column(String(100))
    description = Column(Text)

    # Route definition
    origin_port_id = Column(Integer, ForeignKey("ports.id"), nullable=True)
    destination_port_id = Column(Integer, ForeignKey("ports.id"), nullable=True)
    waypoints = Column(Text)  # JSON: array of {name, lat, lng, type}
    total_distance_km = Column(Float)
    modes = Column(Text)  # JSON: ["truck", "rail", "barge", "vessel"]

    # Commodity
    primary_commodity = Column(String(100))  # iron_ore, copper, bauxite, crude_oil, lng
    annual_volume_mt = Column(Float)  # million tonnes per year

    # Status
    status = Column(String(50), default="active")  # active, seasonal, disrupted, closed

    # Performance metrics
    avg_transit_days = Column(Float)
    avg_demurrage_days = Column(Float)
    avg_cost_per_tonne = Column(Float)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    origin_port = relationship("Port", foreign_keys=[origin_port_id], back_populates="corridors_origin")
    destination_port = relationship("Port", foreign_keys=[destination_port_id], back_populates="corridors_destination")
    shipments = relationship("Shipment", back_populates="corridor")
    assets = relationship("Asset", back_populates="corridor")
    freight_rates = relationship("FreightRate", back_populates="corridor")
    geofences = relationship("Geofence", back_populates="corridor")

    def __repr__(self):
        return f"<Corridor(id={self.id}, name='{self.name}', code='{self.code}')>"


class Geofence(Base):
    __tablename__ = "geofences"

    id = Column(Integer, primary_key=True, index=True)
    corridor_id = Column(Integer, ForeignKey("corridors.id"), nullable=True)
    name = Column(String(255), nullable=False)
    fence_type = Column(String(50))  # corridor, port, restricted, checkpoint, danger_zone
    geometry = Column(Text, nullable=False)  # GeoJSON polygon/circle
    alert_on_enter = Column(Boolean, default=True)
    alert_on_exit = Column(Boolean, default=True)
    alert_on_dwell = Column(Boolean, default=False)
    max_dwell_minutes = Column(Integer)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    corridor = relationship("Corridor", back_populates="geofences")

    def __repr__(self):
        return f"<Geofence(id={self.id}, name='{self.name}', type='{self.fence_type}')>"
