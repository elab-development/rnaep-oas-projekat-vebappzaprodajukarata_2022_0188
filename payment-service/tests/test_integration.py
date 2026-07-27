import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

AUTH_HEADERS = {"X-User-Id": "100", "X-User-Role": "customer"}
ADMIN_HEADERS = {"X-User-Id": "999", "X-User-Role": "admin"}


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
        "payment_method_id": 1,
        "amount": 1500.0,
        "user_email": "test@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    response = client.post("/payments", json=payment_data, headers=AUTH_HEADERS)
    assert response.status_code == 200

    data = response.json()
    assert data["reservation_id"] == 1
    assert data["user_id"] == 100
    assert data["amount"] == 1500.0
    assert data["status"] == "paid"


def test_create_payment_no_auth(mock_kafka):
    payment_data = {
        "reservation_id": 1,
        "payment_method_id": 1,
        "amount": 1500.0,
        "user_email": "test@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    response = client.post("/payments", json=payment_data)
    assert response.status_code == 401


def test_get_all_payments_owner_only_sees_own(mock_kafka):
    payment_data = {
        "reservation_id": 2,
        "payment_method_id": 1,
        "amount": 500.0,
        "user_email": "test2@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    client.post("/payments", json=payment_data, headers=AUTH_HEADERS)

    response = client.get("/payments", headers=AUTH_HEADERS)
    assert response.status_code == 200
    for payment in response.json():
        assert payment["user_id"] == 100


def test_get_all_payments_admin_sees_all(mock_kafka):
    payment_data = {
        "reservation_id": 3,
        "payment_method_id": 1,
        "amount": 500.0,
        "user_email": "test3@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    client.post("/payments", json=payment_data, headers=AUTH_HEADERS)

    response = client.get("/payments", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_payment_by_id_owner(mock_kafka):
    payment_data = {
        "reservation_id": 4,
        "payment_method_id": 1,
        "amount": 750.0,
        "user_email": "test4@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    create_response = client.post("/payments", json=payment_data, headers=AUTH_HEADERS)
    payment_id = create_response.json()["id"]

    response = client.get(f"/payments/{payment_id}", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json()["id"] == payment_id


def test_get_payment_by_id_forbidden_for_other_user(mock_kafka):
    payment_data = {
        "reservation_id": 5,
        "payment_method_id": 1,
        "amount": 750.0,
        "user_email": "test5@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    create_response = client.post("/payments", json=payment_data, headers=AUTH_HEADERS)
    payment_id = create_response.json()["id"]

    other_user_headers = {"X-User-Id": "200", "X-User-Role": "customer"}
    response = client.get(f"/payments/{payment_id}", headers=other_user_headers)
    assert response.status_code == 403


def test_get_payment_by_id_allowed_for_admin(mock_kafka):
    payment_data = {
        "reservation_id": 6,
        "payment_method_id": 1,
        "amount": 750.0,
        "user_email": "test6@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    create_response = client.post("/payments", json=payment_data, headers=AUTH_HEADERS)
    payment_id = create_response.json()["id"]

    response = client.get(f"/payments/{payment_id}", headers=ADMIN_HEADERS)
    assert response.status_code == 200


def test_get_payment_no_auth_headers(mock_kafka):
    payment_data = {
        "reservation_id": 7,
        "payment_method_id": 1,
        "amount": 750.0,
        "user_email": "test7@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    create_response = client.post("/payments", json=payment_data, headers=AUTH_HEADERS)
    payment_id = create_response.json()["id"]

    response = client.get(f"/payments/{payment_id}")
    assert response.status_code == 401


def test_get_payment_not_found(mock_kafka):
    response = client.get("/payments/999", headers=AUTH_HEADERS)
    assert response.status_code == 404
    assert response.json() == {"detail": "Payment not found"}


def test_create_refund_success(mock_kafka):
    payment_data = {
        "reservation_id": 8,
        "payment_method_id": 1,
        "amount": 1000.0,
        "user_email": "test8@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    create_response = client.post("/payments", json=payment_data, headers=AUTH_HEADERS)
    payment_id = create_response.json()["id"]

    refund_data = {
        "payment_id": payment_id,
        "amount": 1000.0,
        "user_email": "test8@example.com"
    }
    response = client.post("/refunds", json=refund_data, headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_create_refund_forbidden_for_other_user(mock_kafka):
    payment_data = {
        "reservation_id": 9,
        "payment_method_id": 1,
        "amount": 1000.0,
        "user_email": "test9@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    create_response = client.post("/payments", json=payment_data, headers=AUTH_HEADERS)
    payment_id = create_response.json()["id"]

    refund_data = {
        "payment_id": payment_id,
        "amount": 1000.0,
        "user_email": "test9@example.com"
    }
    other_user_headers = {"X-User-Id": "200", "X-User-Role": "customer"}
    response = client.post("/refunds", json=refund_data, headers=other_user_headers)
    assert response.status_code == 403


def test_create_refund_payment_not_found(mock_kafka):
    refund_data = {
        "payment_id": 999,
        "amount": 100.0,
        "user_email": "test@example.com"
    }
    response = client.post("/refunds", json=refund_data, headers=AUTH_HEADERS)
    assert response.status_code == 404


def test_get_all_transactions_owner_only_sees_own(mock_kafka):
    payment_data = {
        "reservation_id": 10,
        "payment_method_id": 1,
        "amount": 300.0,
        "user_email": "test10@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    client.post("/payments", json=payment_data, headers=AUTH_HEADERS)

    response = client.get("/transactions", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_transaction_by_id_forbidden_for_other_user(mock_kafka):
    payment_data = {
        "reservation_id": 11,
        "payment_method_id": 1,
        "amount": 300.0,
        "user_email": "test11@example.com",
        "event_name": "Taylor Swift Concert",
        "event_date": "2026-06-15T20:00:00",
        "venue_name": "Stark Arena",
        "venue_address": "Beograd"
    }
    client.post("/payments", json=payment_data, headers=AUTH_HEADERS)

    transactions_response = client.get("/transactions", headers=AUTH_HEADERS)
    transaction_id = transactions_response.json()[0]["id"]

    other_user_headers = {"X-User-Id": "200", "X-User-Role": "customer"}
    response = client.get(f"/transactions/{transaction_id}", headers=other_user_headers)
    assert response.status_code == 403