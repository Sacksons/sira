"""
Health Check Tests
"""

import pytest
from fastapi import status


class TestHealth:
    """Test health and root endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data

    def test_openapi_docs(self, client):
        """Test OpenAPI documentation endpoint"""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK

    def test_openapi_json(self, client):
        """Test OpenAPI JSON endpoint"""
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
