import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.department import Department
from app.models.user import User, UserRole
from app.utils.security import hash_password

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def department(db_session):
    dept = Department(name="CSE", description="Computer Science", is_active=True)
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


@pytest.fixture
def user_token(client, department):
    client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "user@example.com",
            "phone": "9000000001",
            "password": "Passw0rd!",
            "department_id": department.id,
        },
    )
    resp = client.post("/auth/login", json={"email": "user@example.com", "password": "Passw0rd!"})
    return resp.json()["access_token"]


@pytest.fixture
def admin_token(db_session, client, department):
    admin = User(
        name="Admin",
        email="admin@example.com",
        phone="9000000002",
        password_hash=hash_password("AdminPass1!"),
        department_id=department.id,
        role=UserRole.admin,
    )
    db_session.add(admin)
    db_session.commit()
    resp = client.post("/auth/login", json={"email": "admin@example.com", "password": "AdminPass1!"})
    return resp.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}
