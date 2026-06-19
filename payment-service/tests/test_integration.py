import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_kafka():
    with patch('main.send_payment_completed') as mock_completed, \
         patch('main.send_payment_failed') as mock_failed, \
         patch('main.send_payment_refunded') as mock_refunded:
        yield mock_completed, mock_failed, mock_refunded


def test_create_payment_success(mock_kafka):
    payment_data = {
        "reservation_id": 1,
        "payment_method_id": 1,
        "amount": 1500.0,
        "user_email": "test@example.com"
    }
    response = client.post("/payments", json=payment_data)
    assert response.status_code == 200

    data = response.json()
    assert data["reservation_id"] == 1
    assert data["amount"] == 1500.0
    assert data["status"] == "paid"


def test_get_all_payments(mock_kafka):
    payment_data = {
        "reservation_id": 2,
        "payment_method_id": 1,
        "amount": 500.0,
        "user_email": "test2@example.com"
    }
    client.post("/payments", json=payment_data)

    response = client.get("/payments")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_payment_by_id(mock_kafka):
    payment_data = {
        "reservation_id": 3,
        "payment_method_id": 1,
        "amount": 750.0,
        "user_email": "test3@example.com"
    }
    create_response = client.post("/payments", json=payment_data)
    payment_id = create_response.json()["id"]

    response = client.get(f"/payments/{payment_id}")
    assert response.status_code == 200
    assert response.json()["id"] == payment_id


def test_get_payment_not_found(mock_kafka):
    response = client.get("/payments/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Payment not found"}


def test_create_refund_success(mock_kafka):
    payment_data = {
        "reservation_id": 4,
        "payment_method_id": 1,
        "amount": 1000.0,
        "user_email": "test4@example.com"
    }
    create_response = client.post("/payments", json=payment_data)
    payment_id = create_response.json()["id"]

    refund_data = {
        "payment_id": payment_id,
        "amount": 1000.0,
        "user_email": "test4@example.com"
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
        "reservation_id": 5,
        "payment_method_id": 1,
        "amount": 300.0,
        "user_email": "test5@example.com"
    }
    client.post("/payments", json=payment_data)

    response = client.get("/transactions")
    assert response.status_code == 200
    assert len(response.json()) >= 1

