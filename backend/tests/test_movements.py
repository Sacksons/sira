"""
Movement Tests
"""

import pytest
from fastapi import status
from datetime import datetime, timezone, timedelta


class TestMovements:
    """Test movement endpoints"""

    def test_create_movement(self, client, auth_headers):
        """Test creating a movement"""
        movement_data = {
            "cargo": "Container XYZ-123",
            "route": "Singapore -> Rotterdam",
            "assets": "Vessel: MV Test",
            "stakeholders": "Shipper: Test Corp",
            "laycan_start": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "laycan_end": (datetime.now(timezone.utc) + timedelta(days=15)).isoformat()
        }
        response = client.post(
            "/api/v1/movements/",
            json=movement_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["cargo"] == "Container XYZ-123"
        assert data["status"] == "active"

    def test_create_movement_invalid_dates(self, client, auth_headers):
        """Test creating movement with invalid date range"""
        movement_data = {
            "cargo": "Container XYZ-123",
            "route": "Singapore -> Rotterdam",
            "laycan_start": (datetime.now(timezone.utc) + timedelta(days=15)).isoformat(),
            "laycan_end": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        }
        response = client.post(
            "/api/v1/movements/",
            json=movement_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_movements(self, client, auth_headers):
        """Test listing movements"""
        # Create a movement first
        movement_data = {
            "cargo": "Test Cargo",
            "route": "A -> B",
            "laycan_start": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "laycan_end": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
        }
        client.post("/api/v1/movements/", json=movement_data, headers=auth_headers)

        response = client.get("/api/v1/movements/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1

    def test_get_movement(self, client, auth_headers):
        """Test getting a specific movement"""
        # Create a movement first
        movement_data = {
            "cargo": "Test Cargo",
            "route": "A -> B",
            "laycan_start": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "laycan_end": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
        }
        create_response = client.post(
            "/api/v1/movements/",
            json=movement_data,
            headers=auth_headers
        )
        movement_id = create_response.json()["id"]

        response = client.get(f"/api/v1/movements/{movement_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == movement_id

    def test_get_movement_not_found(self, client, auth_headers):
        """Test getting non-existent movement"""
        response = client.get("/api/v1/movements/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_movement(self, client, auth_headers):
        """Test updating a movement"""
        # Create a movement first
        movement_data = {
            "cargo": "Original Cargo",
            "route": "A -> B",
            "laycan_start": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "laycan_end": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
        }
        create_response = client.post(
            "/api/v1/movements/",
            json=movement_data,
            headers=auth_headers
        )
        movement_id = create_response.json()["id"]

        # Update the movement
        update_data = {"cargo": "Updated Cargo", "status": "completed"}
        response = client.put(
            f"/api/v1/movements/{movement_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["cargo"] == "Updated Cargo"
        assert response.json()["status"] == "completed"
