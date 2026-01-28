"""
API v1 Routes
"""

from fastapi import APIRouter
from app.api.v1 import auth, users, movements, events, alerts, cases, playbooks, evidences, notifications, reports, websocket

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(movements.router, prefix="/movements", tags=["Movements"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(cases.router, prefix="/cases", tags=["Cases"])
api_router.include_router(playbooks.router, prefix="/playbooks", tags=["Playbooks"])
api_router.include_router(evidences.router, prefix="/evidences", tags=["Evidence"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
