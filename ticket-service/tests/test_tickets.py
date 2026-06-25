import os

os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test_ticket_service.db"

if os.path.exists("test_ticket_service.db"):
    os.remove("test_ticket_service.db")

from fastapi.testclient import TestClient
from app.main import app
from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Ticket Service is running"


def test_get_all_tickets():
    response = client.get("/tickets/")
    assert response.status_code == 200


def test_ticket_not_found():
    response = client.get("/tickets/999999")
    assert response.status_code == 404