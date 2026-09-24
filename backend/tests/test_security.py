import time

import pytest

from app.core.security import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password_roundtrip():
    hashed = hash_password("mypassword")
    assert hashed != "mypassword"
    assert verify_password("mypassword", hashed)
    assert not verify_password("wrongpassword", hashed)


def test_access_token_roundtrip():
    token = create_access_token(user_id=42)
    assert decode_token(token, expected_type="access") == 42


def test_refresh_token_roundtrip():
    token = create_refresh_token(user_id=7)
    assert decode_token(token, expected_type="refresh") == 7


def test_access_token_rejected_as_refresh():
    token = create_access_token(user_id=1)
    with pytest.raises(InvalidTokenError):
        decode_token(token, expected_type="refresh")


def test_garbage_token_rejected():
    with pytest.raises(InvalidTokenError):
        decode_token("not-a-real-token", expected_type="access")
