import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_kafka():
    # Mockujemo sve Kafka funkcije da test ne pokušava pravu konekciju
    with patch('main.send_payment_completed') as mock_completed, \
         patch('main.send_payment_failed') as mock_failed, \
         patch('main.send_payment_refunded') as mock_refunded:
        yield mock_completed, mock_failed, mock_refunded


def test_create_payment_success(mock_kafka):
    payment_data = {
        "reservation_id": 1,
        "user_id": 100,
        "payment_method_id": 1,
        "amount": 1500.0,
        "user_email": "test@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    response = client.post("/payments", json=payment_data)
    assert response.status_code == 200

    data = response.json()
    assert data["reservation_id"] == 1
    assert data["user_id"] == 100
    assert data["amount"] == 1500.0
    assert data["status"] == "paid"


def test_get_all_payments(mock_kafka):
    payment_data = {
        "reservation_id": 2,
        "user_id": 100,
        "payment_method_id": 1,
        "amount": 500.0,
        "user_email": "test2@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    client.post("/payments", json=payment_data)

    response = client.get("/payments")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_payment_by_id_owner(mock_kafka):
    payment_data = {
        "reservation_id": 3,
        "user_id": 100,
        "payment_method_id": 1,
        "amount": 750.0,
        "user_email": "test3@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    create_response = client.post("/payments", json=payment_data)
    payment_id = create_response.json()["id"]

    response = client.get(
        f"/payments/{payment_id}",
        headers={"X-User-Id": "100", "X-User-Role": "customer"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == payment_id


def test_get_payment_by_id_forbidden_for_other_user(mock_kafka):
    payment_data = {
        "reservation_id": 4,
        "user_id": 100,
        "payment_method_id": 1,
        "amount": 750.0,
        "user_email": "test4@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    create_response = client.post("/payments", json=payment_data)
    payment_id = create_response.json()["id"]

    # Drugi korisnik (id 200) pokušava da vidi tuđe plaćanje
    response = client.get(
        f"/payments/{payment_id}",
        headers={"X-User-Id": "200", "X-User-Role": "customer"}
    )
    assert response.status_code == 403


def test_get_payment_by_id_allowed_for_admin(mock_kafka):
    payment_data = {
        "reservation_id": 5,
        "user_id": 100,
        "payment_method_id": 1,
        "amount": 750.0,
        "user_email": "test5@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    create_response = client.post("/payments", json=payment_data)
    payment_id = create_response.json()["id"]

    # Admin moze da vidi bilo cije plaćanje
    response = client.get(
        f"/payments/{payment_id}",
        headers={"X-User-Id": "999", "X-User-Role": "admin"}
    )
    assert response.status_code == 200


def test_get_payment_no_auth_headers(mock_kafka):
    payment_data = {
        "reservation_id": 6,
        "user_id": 100,
        "payment_method_id": 1,
        "amount": 750.0,
        "user_email": "test6@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    create_response = client.post("/payments", json=payment_data)
    payment_id = create_response.json()["id"]

    # Bez header-a, treba 401
    response = client.get(f"/payments/{payment_id}")
    assert response.status_code == 401


def test_get_payment_not_found(mock_kafka):
    response = client.get(
        "/payments/999",
        headers={"X-User-Id": "100", "X-User-Role": "customer"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Payment not found"}


def test_create_refund_success(mock_kafka):
    payment_data = {
        "reservation_id": 7,
        "user_id": 100,
        "payment_method_id": 1,
        "amount": 1000.0,
        "user_email": "test7@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    create_response = client.post("/payments", json=payment_data)
    payment_id = create_response.json()["id"]

    refund_data = {
        "payment_id": payment_id,
        "amount": 1000.0,
        "user_email": "test7@example.com"
    }
    response = client.post("/refunds", json=refund_data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_create_refund_payment_not_found(mock_kafka):
    refund_data = {
        "payment_id": 999,
        "amount": 100.0,
        "user_email": "test@example.com"
    }
    response = client.post("/refunds", json=refund_data)
    assert response.status_code == 404


def test_get_all_transactions(mock_kafka):
    payment_data = {
        "reservation_id": 8,
        "user_id": 100,
        "payment_method_id": 1,
        "amount": 300.0,
        "user_email": "test8@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    client.post("/payments", json=payment_data)

    response = client.get("/transactions")
    assert response.status_code == 200
    assert len(response.json()) >= 1