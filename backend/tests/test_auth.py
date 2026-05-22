from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.core.auth import (
    create_access_token,
    decode_token,
    get_current_user,
    hash_password,
    require_admin,
    verify_password,
)


def test_password_hash_and_verify():
    hashed = hash_password("demo-password")

    assert hashed != "demo-password"
    assert verify_password("demo-password", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_create_access_token():
    token = create_access_token({"sub": "user-1", "role": "ADMIN"})

    assert isinstance(token, str)
    assert token


def test_decode_token_and_dependency_helpers():
    token = create_access_token({"sub": "admin-1", "role": "ADMIN"}, expires_minutes=5)

    decoded = decode_token(token)

    assert decoded["sub"] == "admin-1"
    assert get_current_user(SimpleNamespace(credentials=token))["role"] == "ADMIN"
    assert require_admin(decoded) == decoded


def test_auth_errors_are_reported_as_http_exceptions():
    with pytest.raises(HTTPException) as invalid_token:
        decode_token("not-a-jwt")

    with pytest.raises(HTTPException) as forbidden:
        require_admin({"sub": "operator-1", "role": "OPERATOR"})

    assert invalid_token.value.status_code == 401
    assert invalid_token.value.detail["code"] == "AUTH_ERROR"
    assert forbidden.value.status_code == 403
    assert forbidden.value.detail["code"] == "FORBIDDEN_ERROR"
