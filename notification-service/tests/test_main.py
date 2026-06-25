from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Notification Service is running"}


@patch('main.email_logs')
def test_get_notifications_no_auth_headers(mock_email_logs):
    response = client.get("/notifications")
    assert response.status_code == 401


@patch('main.email_logs')
def test_get_notifications_as_owner(mock_email_logs):
    mock_email_logs.find.return_value = [{'order_id': 1, 'user_id': 100}]

    response = client.get(
        "/notifications",
        headers={"X-User-Id": "100", "X-User-Role": "customer"}
    )
    assert response.status_code == 200
    mock_email_logs.find.assert_called_once_with({'user_id': 100}, {'_id': 0})


@patch('main.email_logs')
def test_get_notifications_as_admin(mock_email_logs):
    mock_email_logs.find.return_value = [{'order_id': 1, 'user_id': 100}, {'order_id': 2, 'user_id': 200}]

    response = client.get(
        "/notifications",
        headers={"X-User-Id": "999", "X-User-Role": "admin"}
    )
    assert response.status_code == 200
    mock_email_logs.find.assert_called_once_with({}, {'_id': 0})