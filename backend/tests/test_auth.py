from app.core.auth import create_access_token, hash_password, verify_password


def test_password_hash_and_verify():
    hashed = hash_password("demo-password")

    assert hashed != "demo-password"
    assert verify_password("demo-password", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_create_access_token():
    token = create_access_token({"sub": "user-1", "role": "ADMIN"})

    assert isinstance(token, str)
    assert token
