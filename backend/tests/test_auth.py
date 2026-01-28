"""
Authentication Tests
"""

import pytest
from fastapi import status


class TestAuthentication:
    """Test authentication endpoints"""

    def test_login_success(self, client, admin_user):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "adminpass123"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, admin_user):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "wrongpassword"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "nonexistent", "password": "password"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user(self, client, auth_headers):
        """Test getting current user info"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"

    def test_get_current_user_no_auth(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_register_user(self, client):
        """Test user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@test.com",
                "password": "newuserpass123"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "newuser"
        assert data["role"] == "operator"  # Default role

    def test_register_duplicate_username(self, client, admin_user):
        """Test registration with duplicate username"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "admin",
                "email": "another@test.com",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
