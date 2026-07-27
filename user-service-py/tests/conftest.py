"""
Podešavanje testova - koristi SQLite bazu u memoriji (ne treba MySQL).
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models import Role, User
from app.security import hash_password

# Test baza - SQLite u memoriji
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Pre svakog testa: napravi svežu bazu sa ulogama. Posle: obriši."""
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    for name in ["guest", "user", "admin"]:
        db.add(Role(name=name, description=name))
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def make_user():
    """Pomoćna fixtura za kreiranje korisnika u test bazi."""
    def _make(email="test@example.com", password="Password123!", role="user", name="Test"):
        db = TestingSessionLocal()
        user = User(name=name, email=email, password=hash_password(password))
        role_obj = db.query(Role).filter(Role.name == role).first()
        if role_obj:
            user.roles.append(role_obj)
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id
        db.close()
        return user_id
    return _make
