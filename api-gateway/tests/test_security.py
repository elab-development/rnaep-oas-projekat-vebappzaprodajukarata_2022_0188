import os
os.environ["SECRET_KEY"] = "promeni-ovaj-tajni-kljuc-u-produkciji-mora-biti-dugacak"
os.environ["ALGORITHM"] = "HS256"
os.environ["USER_SERVICE_URL"] = "http://user-service:8000"

from unittest.mock import patch, MagicMock
from jose import jwt
import pytest
from fastapi import HTTPException

from security import decode_token, get_user_role


def create_test_token(user_id: int):
    return jwt.encode({"sub": str(user_id)}, "promeni-ovaj-tajni-kljuc-u-produkciji-mora-biti-dugacak", algorithm="HS256")


def test_decode_token_valid():
    token = create_test_token(123)
    user_id = decode_token(authorization=f"Bearer {token}")
    assert user_id == 123


def test_decode_token_missing_header():
    with pytest.raises(HTTPException) as exc_info:
        decode_token(authorization=None)
    assert exc_info.value.status_code == 401


def test_decode_token_invalid_format():
    with pytest.raises(HTTPException) as exc_info:
        decode_token(authorization="InvalidFormat token")
    assert exc_info.value.status_code == 401


def test_decode_token_invalid_token():
    with pytest.raises(HTTPException) as exc_info:
        decode_token(authorization="Bearer invalid.token.here")
    assert exc_info.value.status_code == 401


@patch('security.httpx.get')
def test_get_user_role_admin(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"roles": ["admin", "user"]}
    mock_get.return_value = mock_response

    role = get_user_role(authorization="Bearer some-token")
    assert role == "admin"


@patch('security.httpx.get')
def test_get_user_role_regular_user(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"roles": ["user"]}
    mock_get.return_value = mock_response

    role = get_user_role(authorization="Bearer some-token")
    assert role == "user"


@patch('security.httpx.get')
def test_get_user_role_unauthorized(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_get.return_value = mock_response

    with pytest.raises(HTTPException) as exc_info:
        get_user_role(authorization="Bearer invalid-token")
    assert exc_info.value.status_code == 401