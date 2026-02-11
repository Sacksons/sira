#!/usr/bin/env python3
"""
SIRA Platform - Local Development Setup
Creates database tables, admin user, and seed data for local development.
Usage: python setup_dev.py
"""

import os
import sys

# Ensure .env exists with SQLite config (fix PostgreSQL errors automatically)
ENV_CONTENT = (
    "# SIRA Platform - Local Development Environment\n"
    "APP_NAME=SIRA Platform\n"
    "APP_VERSION=2.0.0\n"
    "DEBUG=True\n"
    "LOG_LEVEL=INFO\n"
    "DATABASE_URL=sqlite:///./sira_dev.db\n"
    "SECRET_KEY=dev-secret-key-change-in-production-min-32-chars-long\n"
    "ALGORITHM=HS256\n"
    "ACCESS_TOKEN_EXPIRE_MINUTES=120\n"
    "ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000\n"
)

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
needs_fix = False

if not os.path.exists(env_path):
    needs_fix = True
    print("[AUTO] No .env file found.")
else:
    # Check if existing .env has PostgreSQL (which won't work without a PG server)
    with open(env_path, "r") as f:
        content = f.read()
    if "postgresql://" in content:
        needs_fix = True
        print("[AUTO] .env has PostgreSQL config. Switching to SQLite for local dev...")

if needs_fix:
    with open(env_path, "w") as f:
        f.write(ENV_CONTENT)
    print(f"[AUTO] Created {env_path} with SQLite configuration.")

from dotenv import load_dotenv
load_dotenv()

from app.core.database import Base, engine, SessionLocal
from app.core.security import hash_password
from app.models import *  # noqa: Import all models to register with Base
from datetime import datetime, timedelta, timezone


def setup():
    print("=" * 60)
    print("SIRA Platform - Development Setup")
    print("=" * 60)

    # Create all tables
    print("\n[1/3] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("  -> Tables created successfully")

    db = SessionLocal()

    # Create admin user
    print("\n[2/3] Creating admin user...")
    existing = db.query(User).filter(User.username == "admin").first()
    if existing:
        print("  -> Admin user already exists, skipping")
    else:
        admin = User(
            username="admin",
            email="admin@sira.com",
            full_name="SIRA Administrator",
            hashed_password=hash_password("admin123"),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print("  -> Admin user created (username: admin, password: admin123)")

    # Seed demo data
    print("\n[3/3] Seeding demo data...")
    now = datetime.now(timezone.utc)

    # Ports
    if db.query(Port).count() == 0:
        ports = [
            Port(name="Conakry Port", code="GNCKY", country="Guinea", region="West Africa",
                 latitude=9.5092, longitude=-13.7122, port_type="deep_water", max_draft=14.0,
                 status="operational", current_queue=3, avg_wait_days=2.5, avg_dwell_days=4.0,
                 authority="Port Autonome de Conakry", timezone="UTC"),
            Port(name="Kamsar Port", code="GNKMR", country="Guinea", region="West Africa",
                 latitude=10.6477, longitude=-14.6181, port_type="deep_water", max_draft=16.0,
                 status="operational", current_queue=5, avg_wait_days=3.0, avg_dwell_days=5.0,
                 authority="CBG", timezone="UTC"),
            Port(name="Freetown Port", code="SLFNA", country="Sierra Leone", region="West Africa",
                 latitude=8.4897, longitude=-13.2314, port_type="deep_water", max_draft=11.0,
                 status="congested", current_queue=8, avg_wait_days=5.0, avg_dwell_days=6.5,
                 authority="Sierra Leone Ports Authority", timezone="UTC"),
            Port(name="Dakar Port", code="SNDKR", country="Senegal", region="West Africa",
                 latitude=14.6937, longitude=-17.4441, port_type="deep_water", max_draft=13.5,
                 status="operational", current_queue=2, avg_wait_days=1.5, avg_dwell_days=3.0,
                 authority="Port Autonome de Dakar", timezone="UTC"),
            Port(name="Rotterdam Europoort", code="NLRTM", country="Netherlands", region="Europe",
                 latitude=51.9225, longitude=4.4792, port_type="deep_water", max_draft=24.0,
                 status="operational", current_queue=1, avg_wait_days=0.5, avg_dwell_days=2.0,
                 authority="Port of Rotterdam Authority", timezone="CET"),
        ]
        db.add_all(ports)
        db.commit()
        print("  -> 5 ports created")

        # Berths for Conakry
        berths = [
            Berth(port_id=1, name="Berth A1", berth_type="ore", max_draft=14.0, max_loa=250.0,
                  loading_rate=5000, status="available"),
            Berth(port_id=1, name="Berth A2", berth_type="ore", max_draft=12.0, max_loa=200.0,
                  loading_rate=3000, status="occupied"),
            Berth(port_id=1, name="Berth B1", berth_type="general", max_draft=10.0, max_loa=180.0,
                  loading_rate=2000, status="available"),
            Berth(port_id=2, name="CBG Berth 1", berth_type="ore", max_draft=16.0, max_loa=300.0,
                  loading_rate=8000, status="available"),
            Berth(port_id=2, name="CBG Berth 2", berth_type="ore", max_draft=14.0, max_loa=260.0,
                  loading_rate=6000, status="maintenance"),
        ]
        db.add_all(berths)
        db.commit()
        print("  -> 5 berths created")

    # Corridors
    if db.query(Corridor).count() == 0:
        corridors = [
            Corridor(name="Guinea Bauxite Corridor", code="GN-BXE-01",
                     corridor_type="mining", country="Guinea", region="West Africa",
                     description="Sangaredi mine to Kamsar port bauxite export corridor",
                     origin_port_id=2, total_distance_km=135,
                     modes='["rail", "barge", "vessel"]', primary_commodity="bauxite",
                     annual_volume_mt=15.0, status="active",
                     avg_transit_days=3, avg_demurrage_days=2.5, avg_cost_per_tonne=12.5),
            Corridor(name="Simandou Iron Ore Corridor", code="GN-FE-01",
                     corridor_type="mining", country="Guinea", region="West Africa",
                     description="Simandou mine to Conakry deep water port",
                     origin_port_id=1, total_distance_km=650,
                     modes='["rail", "vessel"]', primary_commodity="iron_ore",
                     annual_volume_mt=60.0, status="active",
                     avg_transit_days=5, avg_demurrage_days=3.0, avg_cost_per_tonne=18.0),
            Corridor(name="Sierra Leone Rutile Corridor", code="SL-RUT-01",
                     corridor_type="mining", country="Sierra Leone", region="West Africa",
                     description="Rutile mine to Freetown port",
                     origin_port_id=3, total_distance_km=180,
                     modes='["truck", "vessel"]', primary_commodity="rutile",
                     annual_volume_mt=2.0, status="active",
                     avg_transit_days=2, avg_demurrage_days=4.0, avg_cost_per_tonne=22.0),
        ]
        db.add_all(corridors)
        db.commit()
        print("  -> 3 corridors created")

    # Vessels
    if db.query(Vessel).count() == 0:
        vessels = [
            Vessel(name="MV African Pioneer", imo_number="9876543", mmsi="636012345",
                   vessel_type="bulk_carrier", flag="Liberia", dwt=82000, loa=229.0,
                   beam=32.2, draft=14.2, year_built=2018, owner="Africa Bulk Shipping",
                   status="active", current_lat=9.8, current_lng=-14.1,
                   current_speed=8.5, current_heading=225, current_destination="GNCKY",
                   position_updated_at=now, charter_type="time_charter", charter_rate=18000),
            Vessel(name="MV Sahel Express", imo_number="9876544", mmsi="636012346",
                   vessel_type="bulk_carrier", flag="Marshall Islands", dwt=58000, loa=190.0,
                   beam=32.2, draft=12.8, year_built=2020, owner="West Coast Carriers",
                   status="active", current_lat=14.2, current_lng=-17.8,
                   current_speed=11.2, current_heading=180, current_destination="GNKMR",
                   position_updated_at=now, charter_type="voyage_charter", charter_rate=22000),
            Vessel(name="MV Mineral Queen", imo_number="9876545", mmsi="636012347",
                   vessel_type="bulk_carrier", flag="Panama", dwt=120000, loa=260.0,
                   beam=43.0, draft=16.5, year_built=2015, owner="Global Ore Transport",
                   status="idle", current_lat=10.6, current_lng=-14.6,
                   current_speed=0, current_heading=0, current_destination="GNKMR",
                   position_updated_at=now, charter_type="owned"),
        ]
        db.add_all(vessels)
        db.commit()
        print("  -> 3 vessels created")

    # Assets
    if db.query(Asset).count() == 0:
        assets = [
            Asset(asset_code="TRK-001", name="Volvo FH16 #1", asset_type="truck",
                  sub_type="flatbed", capacity=30, status="in_transit",
                  current_location="En route Sangaredi", current_lat=11.08, current_lng=-13.84,
                  utilization_pct=78, total_trips=245, assigned_corridor_id=1),
            Asset(asset_code="TRK-002", name="Volvo FH16 #2", asset_type="truck",
                  sub_type="flatbed", capacity=30, status="available",
                  current_location="Conakry Yard", current_lat=9.51, current_lng=-13.71,
                  utilization_pct=65, total_trips=198),
            Asset(asset_code="TRK-003", name="Mercedes Actros #1", asset_type="truck",
                  sub_type="tanker", capacity=25, status="maintenance",
                  current_location="Conakry Workshop", utilization_pct=55, total_trips=156),
            Asset(asset_code="RW-001", name="Rail Wagon A1", asset_type="rail_wagon",
                  sub_type="hopper", capacity=80, status="in_transit",
                  current_location="Simandou Line", utilization_pct=82, total_trips=520,
                  assigned_corridor_id=2),
            Asset(asset_code="RW-002", name="Rail Wagon A2", asset_type="rail_wagon",
                  sub_type="hopper", capacity=80, status="available",
                  utilization_pct=75, total_trips=480),
            Asset(asset_code="BRG-001", name="Barge Kamsar-1", asset_type="barge",
                  capacity=3000, status="in_transit",
                  current_location="Kamsar Channel", current_lat=10.65, current_lng=-14.62,
                  utilization_pct=70, total_trips=89, assigned_corridor_id=1),
            Asset(asset_code="CRN-001", name="Liebherr LHM 550", asset_type="crane",
                  sub_type="mobile_harbour", capacity=144, status="available",
                  current_location="Conakry Port", utilization_pct=60, total_trips=0),
        ]
        db.add_all(assets)
        db.commit()
        print("  -> 7 assets created")

    # Shipments
    if db.query(Shipment).count() == 0:
        shipments = [
            Shipment(shipment_ref="SHP-2026-001", corridor_id=1, vessel_id=1,
                     cargo_type="bauxite", volume_tonnes=75000, origin="Sangaredi Mine",
                     destination="Rotterdam", origin_port_id=2, destination_port_id=5,
                     laycan_start=now - timedelta(days=2), laycan_end=now + timedelta(days=5),
                     status="loading", current_leg="port_loading", current_mode="vessel",
                     eta_destination=now + timedelta(days=18), eta_confidence=0.72,
                     eta_updated_at=now, demurrage_risk_score=45, demurrage_exposure_usd=36000,
                     demurrage_rate_usd=18000, shipper="Guinea Alumina Corp",
                     receiver="Alunorte Netherlands", loading_started=now - timedelta(hours=12)),
            Shipment(shipment_ref="SHP-2026-002", corridor_id=2, vessel_id=2,
                     cargo_type="iron_ore", volume_tonnes=55000, origin="Simandou",
                     destination="Qingdao", laycan_start=now + timedelta(days=3),
                     laycan_end=now + timedelta(days=10), status="in_transit",
                     current_leg="rail_to_port", current_mode="rail",
                     eta_destination=now + timedelta(days=30), eta_confidence=0.58,
                     demurrage_risk_score=72, demurrage_exposure_usd=88000,
                     demurrage_rate_usd=22000, shipper="Simandou Mining SA",
                     receiver="Baoshan Iron & Steel"),
            Shipment(shipment_ref="SHP-2026-003", corridor_id=3,
                     cargo_type="rutile", volume_tonnes=12000, origin="Sierra Rutile Mine",
                     destination="Rotterdam", origin_port_id=3, destination_port_id=5,
                     laycan_start=now + timedelta(days=7), laycan_end=now + timedelta(days=14),
                     status="planned", current_mode="truck",
                     demurrage_risk_score=25, demurrage_exposure_usd=8000,
                     demurrage_rate_usd=15000, shipper="Sierra Rutile Ltd",
                     receiver="Tronox Holdings"),
            Shipment(shipment_ref="SHP-2026-004", corridor_id=1, vessel_id=3,
                     cargo_type="bauxite", volume_tonnes=110000, origin="Sangaredi Mine",
                     destination="Qingdao", origin_port_id=2,
                     laycan_start=now - timedelta(days=5), laycan_end=now - timedelta(days=1),
                     status="at_port", current_leg="anchorage_wait", current_mode="vessel",
                     eta_destination=now + timedelta(days=25), eta_confidence=0.45,
                     demurrage_risk_score=88, demurrage_exposure_usd=132000,
                     demurrage_rate_usd=22000, demurrage_days=3.5,
                     shipper="CBG", receiver="Chalco Aluminum"),
        ]
        db.add_all(shipments)
        db.commit()
        print("  -> 4 shipments created")

        # Milestones for SHP-2026-001
        milestones = [
            ShipmentMilestone(shipment_id=1, milestone_type="mine_dispatch",
                              description="Bauxite dispatched from Sangaredi",
                              location="Sangaredi Mine", mode="rail",
                              planned_time=now - timedelta(days=3),
                              actual_time=now - timedelta(days=3, hours=2),
                              variance_hours=-2.0, status="completed"),
            ShipmentMilestone(shipment_id=1, milestone_type="rail_arrival_port",
                              description="Arrived at Kamsar port rail terminal",
                              location="Kamsar Port", mode="rail",
                              planned_time=now - timedelta(days=2),
                              actual_time=now - timedelta(days=2, hours=4),
                              variance_hours=4.0, status="completed"),
            ShipmentMilestone(shipment_id=1, milestone_type="loading_start",
                              description="Vessel loading commenced",
                              location="Kamsar CBG Berth 1", mode="vessel",
                              planned_time=now - timedelta(hours=14),
                              actual_time=now - timedelta(hours=12),
                              variance_hours=2.0, status="completed"),
            ShipmentMilestone(shipment_id=1, milestone_type="loading_complete",
                              description="Vessel loading complete",
                              location="Kamsar CBG Berth 1", mode="vessel",
                              planned_time=now + timedelta(hours=24),
                              status="pending"),
            ShipmentMilestone(shipment_id=1, milestone_type="departure",
                              description="Vessel departure from Kamsar",
                              location="Kamsar Port", mode="vessel",
                              planned_time=now + timedelta(hours=30),
                              status="pending"),
        ]
        db.add_all(milestones)
        db.commit()
        print("  -> 5 milestones created")

    # Freight Rates
    if db.query(FreightRate).count() == 0:
        rates = [
            FreightRate(corridor_id=1, lane="Kamsar-Rotterdam", mode="vessel",
                        cargo_type="bauxite", rate_usd=14.5, rate_unit="per_tonne",
                        rate_type="spot", source="Baltic Exchange", vessel_class="panamax",
                        effective_date=now - timedelta(days=5)),
            FreightRate(corridor_id=1, lane="Kamsar-Rotterdam", mode="vessel",
                        cargo_type="bauxite", rate_usd=13.8, rate_unit="per_tonne",
                        rate_type="spot", source="Baltic Exchange", vessel_class="panamax",
                        effective_date=now - timedelta(days=15)),
            FreightRate(corridor_id=2, lane="Conakry-Qingdao", mode="vessel",
                        cargo_type="iron_ore", rate_usd=22.0, rate_unit="per_tonne",
                        rate_type="contract", source="Platts", vessel_class="capesize",
                        effective_date=now - timedelta(days=3)),
            FreightRate(corridor_id=1, lane="Sangaredi-Kamsar", mode="rail",
                        cargo_type="bauxite", rate_usd=4.2, rate_unit="per_tonne",
                        rate_type="contract", source="CBG Tariff",
                        effective_date=now - timedelta(days=30)),
            FreightRate(corridor_id=3, lane="SRL Mine-Freetown", mode="truck",
                        cargo_type="rutile", rate_usd=8.5, rate_unit="per_tonne",
                        rate_type="spot", source="Local Market",
                        effective_date=now - timedelta(days=7)),
        ]
        db.add_all(rates)
        db.commit()
        print("  -> 5 freight rates created")

    # Market Indices
    if db.query(MarketIndex).count() == 0:
        indices = [
            MarketIndex(index_name="Baltic Dry Index", index_type="freight",
                        value=1847, unit="points", change_pct=2.3, change_abs=41,
                        period="daily", source="Baltic Exchange", recorded_at=now),
            MarketIndex(index_name="Capesize TCE", index_type="freight",
                        value=18500, unit="USD/day", change_pct=-1.2, change_abs=-225,
                        period="daily", source="Baltic Exchange", recorded_at=now),
            MarketIndex(index_name="Panamax TCE", index_type="freight",
                        value=12800, unit="USD/day", change_pct=0.8, change_abs=100,
                        period="daily", source="Baltic Exchange", recorded_at=now),
            MarketIndex(index_name="Iron Ore 62% Fe", index_type="commodity",
                        value=118.5, unit="USD/tonne", change_pct=-0.5, change_abs=-0.6,
                        period="daily", source="Platts", recorded_at=now),
            MarketIndex(index_name="West Africa Congestion Index", index_type="port_congestion",
                        value=3.2, unit="avg wait days", change_pct=5.0, change_abs=0.15,
                        period="weekly", source="SIRA Analytics", recorded_at=now),
        ]
        db.add_all(indices)
        db.commit()
        print("  -> 5 market indices created")

    db.close()

    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print()
    print("Login credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print()
    print("To start the backend:")
    print("  cd backend")
    print("  source venv/bin/activate")
    print("  uvicorn app.main:app --reload --port 8000")
    print()
    print("To start the frontend:")
    print("  cd frontend")
    print("  npm run dev")
    print()
    print("API Docs:  http://localhost:8000/docs")
    print("Frontend:  http://localhost:5173")
    print()


if __name__ == "__main__":
    setup()
