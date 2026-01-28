"""
Notification Models - Real-time and email notifications
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from datetime import datetime, timezone

from app.core.database import Base


class Notification(Base):
    """Notification records for audit and delivery tracking"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    notification_type = Column(
        String(50),
        nullable=False
    )  # alert, case_update, system, reminder
    channel = Column(String(20), nullable=False)  # websocket, email, sms
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(Text)  # JSON payload
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    is_delivered = Column(Boolean, default=False)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    delivery_error = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.notification_type}', user_id={self.user_id})>"


class NotificationPreference(Base):
    """User notification preferences"""
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # Email preferences
    email_enabled = Column(Boolean, default=True)
    email_critical_alerts = Column(Boolean, default=True)
    email_high_alerts = Column(Boolean, default=True)
    email_medium_alerts = Column(Boolean, default=False)
    email_low_alerts = Column(Boolean, default=False)
    email_case_updates = Column(Boolean, default=True)
    email_daily_digest = Column(Boolean, default=True)

    # WebSocket (real-time) preferences
    websocket_enabled = Column(Boolean, default=True)
    websocket_sound = Column(Boolean, default=True)

    # Quiet hours
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5))  # HH:MM format
    quiet_hours_end = Column(String(5))  # HH:MM format

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<NotificationPreference(user_id={self.user_id})>"
