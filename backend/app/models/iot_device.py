"""
IoT Device & Telemetry Model - Sensors, GPS trackers, and telemetry data
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class IoTDevice(Base):
    __tablename__ = "iot_devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), unique=True, index=True, nullable=False)
    device_type = Column(String(100), nullable=False)  # gps_tracker, temperature_sensor, weight_sensor, seal_sensor, camera, fuel_sensor
    manufacturer = Column(String(255))
    model = Column(String(255))
    firmware_version = Column(String(50))
    sim_iccid = Column(String(30))

    # Assignment
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    vessel_id = Column(Integer, ForeignKey("vessels.id"), nullable=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=True)
    installation_location = Column(String(255))

    # Status
    status = Column(String(50), default="active")  # active, offline, maintenance, decommissioned
    battery_level = Column(Float)  # 0-100
    signal_strength = Column(Float)  # dBm
    last_seen = Column(DateTime(timezone=True))
    last_lat = Column(Float)
    last_lng = Column(Float)

    # Configuration
    reporting_interval_sec = Column(Integer, default=300)  # how often it reports
    alert_thresholds = Column(Text)  # JSON config for alerts

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    telemetry = relationship("TelemetryReading", back_populates="device", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<IoTDevice(id={self.id}, device_id='{self.device_id}', type='{self.device_type}')>"


class TelemetryReading(Base):
    __tablename__ = "telemetry_readings"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("iot_devices.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # Position
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    speed = Column(Float)
    heading = Column(Float)

    # Sensor data
    temperature = Column(Float)
    humidity = Column(Float)
    weight = Column(Float)
    fuel_level = Column(Float)
    battery_level = Column(Float)
    vibration = Column(Float)

    # Seal status
    seal_intact = Column(Boolean)

    # Raw data
    raw_payload = Column(Text)  # JSON raw sensor payload

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    device = relationship("IoTDevice", back_populates="telemetry")

    def __repr__(self):
        return f"<TelemetryReading(device_id={self.device_id}, ts={self.timestamp})>"
