import os

os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test_event_service.db"

if os.path.exists("test_event_service.db"):
    os.remove("test_event_service.db")

from fastapi.testclient import TestClient
from app.main import app
from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Event Service is running"


def test_get_all_events():
    response = client.get("/events/")
    assert response.status_code == 200