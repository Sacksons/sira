"""
Case Tests
"""

import pytest
from fastapi import status


class TestCases:
    """Test case endpoints"""

    def test_create_case(self, client, auth_headers):
        """Test creating a case"""
        case_data = {
            "title": "Security Incident Investigation",
            "overview": "Investigation of suspicious activity",
            "priority": "high",
            "category": "security"
        }
        response = client.post(
            "/api/v1/cases/",
            json=case_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Security Incident Investigation"
        assert data["status"] == "open"
        assert data["case_number"] is not None

    def test_list_cases(self, client, auth_headers):
        """Test listing cases"""
        # Create a case first
        case_data = {"title": "Test Case", "priority": "medium"}
        client.post("/api/v1/cases/", json=case_data, headers=auth_headers)

        response = client.get("/api/v1/cases/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1

    def test_get_case(self, client, auth_headers):
        """Test getting a specific case"""
        # Create a case first
        create_response = client.post(
            "/api/v1/cases/",
            json={"title": "Test Case", "priority": "high"},
            headers=auth_headers
        )
        case_id = create_response.json()["id"]

        response = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == case_id

    def test_update_case(self, client, auth_headers):
        """Test updating a case"""
        # Create a case first
        create_response = client.post(
            "/api/v1/cases/",
            json={"title": "Original Title", "priority": "low"},
            headers=auth_headers
        )
        case_id = create_response.json()["id"]

        # Update the case
        update_data = {
            "title": "Updated Title",
            "priority": "critical",
            "status": "investigating"
        }
        response = client.put(
            f"/api/v1/cases/{case_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["title"] == "Updated Title"
        assert response.json()["priority"] == "critical"

    def test_close_case(self, client, auth_headers):
        """Test closing a case"""
        # Create a case first
        create_response = client.post(
            "/api/v1/cases/",
            json={"title": "Case to Close", "priority": "medium"},
            headers=auth_headers
        )
        case_id = create_response.json()["id"]

        # Close the case
        response = client.post(
            f"/api/v1/cases/{case_id}/close",
            json={
                "closure_code": "resolved",
                "resolution_summary": "Issue resolved",
                "final_costs": 1500.00
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

        # Verify status changed
        get_response = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        assert get_response.json()["status"] == "closed"

    def test_export_case_json(self, client, auth_headers):
        """Test exporting case as JSON"""
        # Create a case first
        create_response = client.post(
            "/api/v1/cases/",
            json={"title": "Case to Export", "priority": "high"},
            headers=auth_headers
        )
        case_id = create_response.json()["id"]

        response = client.get(
            f"/api/v1/cases/{case_id}/export?format=json",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "case" in data
        assert "alerts_count" in data
        assert "evidences_count" in data

    def test_get_case_stats(self, client, auth_headers):
        """Test getting case statistics"""
        # Create some cases
        client.post(
            "/api/v1/cases/",
            json={"title": "Case 1", "priority": "critical"},
            headers=auth_headers
        )
        client.post(
            "/api/v1/cases/",
            json={"title": "Case 2", "priority": "high"},
            headers=auth_headers
        )

        response = client.get("/api/v1/cases/stats", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "open" in data
        assert "by_priority" in data
