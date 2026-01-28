"""
Pytest Configuration and Fixtures
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.security import hash_password
from app.models.user import User


# Test database URL (SQLite in-memory)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_user(db_session):
    """Create an admin user for testing"""
    user = User(
        username="admin",
        email="admin@test.com",
        hashed_password=hash_password("adminpass123"),
        role="admin",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def operator_user(db_session):
    """Create an operator user for testing"""
    user = User(
        username="operator",
        email="operator@test.com",
        hashed_password=hash_password("operatorpass123"),
        role="operator",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_token(client, admin_user):
    """Get admin authentication token"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "adminpass123"}
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def operator_token(client, operator_user):
    """Get operator authentication token"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "operator", "password": "operatorpass123"}
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers(admin_token):
    """Get authorization headers for admin"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="function")
def operator_headers(operator_token):
    """Get authorization headers for operator"""
    return {"Authorization": f"Bearer {operator_token}"}
