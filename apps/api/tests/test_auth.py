"""
JalJasoos API Tests — Phase 2: Authentication & Database

Tests cover:
- Login with valid credentials
- Login with invalid credentials
- Token refresh
- /me endpoint with auth
- Unauthenticated request rejection
- RBAC enforcement
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User, Role, UserRole
from app.core.security import hash_password
from app.models.base import utcnow
import uuid

# ── TEST DATABASE (in-memory SQLite for tests) ─────────────────────────────
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_user(db):
    role = Role(name=UserRole.SUPER_ADMIN, description="Admin")
    db.add(role)
    db.flush()

    user = User(
        email="test_admin@jaljasoos.local",
        full_name="Test Admin",
        hashed_password=hash_password("testpassword"),
        role_id=role.id,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture()
def fm_user(db):
    role = Role(name=UserRole.FACILITY_MANAGER, description="FM")
    db.add(role)
    db.flush()
    user = User(
        email="fm@jaljasoos.local",
        full_name="Facility Manager",
        hashed_password=hash_password("fmpassword"),
        role_id=role.id,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    return user


# ── AUTHENTICATION TESTS ───────────────────────────────────────────────────
class TestAuth:
    def test_login_valid_credentials(self, client, admin_user):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "test_admin@jaljasoos.local", "password": "testpassword"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "SUPER_ADMIN"

    def test_login_invalid_password(self, client, admin_user):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "test_admin@jaljasoos.local", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_unknown_user(self, client):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "nobody@jaljasoos.local", "password": "anypass"},
        )
        assert response.status_code == 401

    def test_token_refresh(self, client, admin_user):
        login_resp = client.post(
            "/api/v1/auth/login",
            data={"username": "test_admin@jaljasoos.local", "password": "testpassword"},
        )
        refresh_token = login_resp.json()["refresh_token"]
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_me_endpoint_authenticated(self, client, admin_user):
        login_resp = client.post(
            "/api/v1/auth/login",
            data={"username": "test_admin@jaljasoos.local", "password": "testpassword"},
        )
        token = login_resp.json()["access_token"]
        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["email"] == "test_admin@jaljasoos.local"

    def test_unauthenticated_request_rejected(self, client):
        response = client.get("/api/v1/nodes/")
        assert response.status_code == 401

    def test_rbac_facility_manager_cannot_delete_society(self, client, fm_user):
        login_resp = client.post(
            "/api/v1/auth/login",
            data={"username": "fm@jaljasoos.local", "password": "fmpassword"},
        )
        token = login_resp.json()["access_token"]
        response = client.delete(
            f"/api/v1/societies/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403


# ── HEALTH ENDPOINT TESTS ──────────────────────────────────────────────────
class TestHealth:
    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
