"""
API v1 Routes
"""

from fastapi import APIRouter
from app.api.v1 import (
    auth, users, movements, events, alerts, cases, playbooks,
    evidences, notifications, reports, websocket,
    vessels, ports, fleet, corridors, shipments, market, control_tower,
)

api_router = APIRouter()

# Original routes
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

# SIRA Platform - Multimodal Control Tower & Logistics Intelligence
api_router.include_router(control_tower.router, prefix="/control-tower", tags=["Control Tower"])
api_router.include_router(vessels.router, prefix="/vessels", tags=["Vessels"])
api_router.include_router(ports.router, prefix="/ports", tags=["Ports & Terminals"])
api_router.include_router(fleet.router, prefix="/fleet", tags=["Fleet & Assets"])
api_router.include_router(corridors.router, prefix="/corridors", tags=["Corridors"])
api_router.include_router(shipments.router, prefix="/shipments", tags=["Shipments"])
api_router.include_router(market.router, prefix="/market", tags=["Market Intelligence"])
