"""
Notification Schemas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class NotificationResponse(BaseModel):
    """Schema for notification response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    notification_type: str
    channel: str
    title: str
    message: str
    data: Optional[str] = None
    priority: str
    is_read: bool
    read_at: Optional[datetime] = None
    is_delivered: bool
    delivered_at: Optional[datetime] = None
    created_at: datetime


class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preferences"""
    email_enabled: Optional[bool] = None
    email_critical_alerts: Optional[bool] = None
    email_high_alerts: Optional[bool] = None
    email_medium_alerts: Optional[bool] = None
    email_low_alerts: Optional[bool] = None
    email_case_updates: Optional[bool] = None
    email_daily_digest: Optional[bool] = None
    websocket_enabled: Optional[bool] = None
    websocket_sound: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = Field(
        None,
        pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    quiet_hours_end: Optional[str] = Field(
        None,
        pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )


class NotificationPreferenceResponse(NotificationPreferenceUpdate):
    """Schema for notification preference response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
