"""
Alert Tests
"""

import pytest
from fastapi import status


class TestAlerts:
    """Test alert endpoints"""

    def test_create_alert(self, client, auth_headers):
        """Test creating an alert"""
        alert_data = {
            "severity": "High",
            "confidence": 0.85,
            "sla_timer": 60,
            "domain": "Maritime Security",
            "description": "Test security alert"
        }
        response = client.post(
            "/api/v1/alerts/",
            json=alert_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["severity"] == "High"
        assert data["status"] == "open"

    def test_create_alert_invalid_severity(self, client, auth_headers):
        """Test creating alert with invalid severity"""
        alert_data = {
            "severity": "Invalid",
            "confidence": 0.85
        }
        response = client.post(
            "/api/v1/alerts/",
            json=alert_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_alert_invalid_confidence(self, client, auth_headers):
        """Test creating alert with invalid confidence"""
        alert_data = {
            "severity": "High",
            "confidence": 1.5  # Should be 0-1
        }
        response = client.post(
            "/api/v1/alerts/",
            json=alert_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_alerts(self, client, auth_headers):
        """Test listing alerts"""
        # Create an alert first
        alert_data = {
            "severity": "Medium",
            "confidence": 0.7,
            "description": "Test alert"
        }
        client.post("/api/v1/alerts/", json=alert_data, headers=auth_headers)

        response = client.get("/api/v1/alerts/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1

    def test_filter_alerts_by_severity(self, client, auth_headers):
        """Test filtering alerts by severity"""
        # Create alerts with different severities
        client.post(
            "/api/v1/alerts/",
            json={"severity": "Critical", "confidence": 0.9},
            headers=auth_headers
        )
        client.post(
            "/api/v1/alerts/",
            json={"severity": "Low", "confidence": 0.5},
            headers=auth_headers
        )

        response = client.get(
            "/api/v1/alerts/?severity=Critical",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for alert in data:
            assert alert["severity"] == "Critical"

    def test_acknowledge_alert(self, client, auth_headers):
        """Test acknowledging an alert"""
        # Create an alert first
        create_response = client.post(
            "/api/v1/alerts/",
            json={"severity": "High", "confidence": 0.8},
            headers=auth_headers
        )
        alert_id = create_response.json()["id"]

        # Acknowledge the alert
        response = client.post(
            f"/api/v1/alerts/{alert_id}/acknowledge",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

        # Verify status changed
        get_response = client.get(f"/api/v1/alerts/{alert_id}", headers=auth_headers)
        assert get_response.json()["status"] == "acknowledged"

    def test_resolve_alert(self, client, auth_headers):
        """Test resolving an alert"""
        # Create an alert first
        create_response = client.post(
            "/api/v1/alerts/",
            json={"severity": "High", "confidence": 0.8},
            headers=auth_headers
        )
        alert_id = create_response.json()["id"]

        # Resolve the alert
        response = client.post(
            f"/api/v1/alerts/{alert_id}/resolve",
            json={"resolution_notes": "False positive"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

        # Verify status changed
        get_response = client.get(f"/api/v1/alerts/{alert_id}", headers=auth_headers)
        assert get_response.json()["status"] == "closed"

    def test_get_alert_stats(self, client, auth_headers):
        """Test getting alert statistics"""
        # Create some alerts
        client.post(
            "/api/v1/alerts/",
            json={"severity": "Critical", "confidence": 0.9},
            headers=auth_headers
        )
        client.post(
            "/api/v1/alerts/",
            json={"severity": "High", "confidence": 0.8},
            headers=auth_headers
        )

        response = client.get("/api/v1/alerts/stats", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "critical" in data
        assert "high" in data
