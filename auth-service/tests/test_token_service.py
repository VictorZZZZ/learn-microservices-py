import uuid

import jwt as pyjwt
import pytest

from app.services.token_service import TokenService

# 32+ байта: PyJWT ругается на более короткие HMAC-ключи (RFC 7518)
TEST_SECRET = "0123456789abcdef0123456789abcdef"
USER_ID = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")


def make_service(access_ttl_minutes: int = 15) -> TokenService:
    return TokenService(
        secret=TEST_SECRET, algorithm="HS256", access_ttl_minutes=access_ttl_minutes
    )


def test_create_and_decode_roundtrip():
    service = make_service()
    token = service.create_access_token(
        user_id=USER_ID,
        username="jdoe",
        roles=["MANAGER"],
        privileges=["CREATE", "READ"],
    )

    payload = service.decode_access_token(token)

    assert payload["sub"] == "jdoe"
    # UUID не умеет сериализоваться в JSON, поэтому в payload лежит строкой
    assert payload["uid"] == str(USER_ID)
    assert payload["roles"] == ["MANAGER"]
    assert payload["privileges"] == ["CREATE", "READ"]
    assert payload["exp"] - payload["iat"] == 15 * 60


def test_expired_token_is_rejected():
    service = make_service(access_ttl_minutes=-1)  # exp уже в прошлом
    token = service.create_access_token(
        user_id=USER_ID, username="jdoe", roles=[], privileges=[]
    )

    with pytest.raises(pyjwt.ExpiredSignatureError):
        service.decode_access_token(token)


def test_token_signed_with_other_secret_is_rejected():
    token = make_service().create_access_token(
        user_id=USER_ID, username="jdoe", roles=[], privileges=[]
    )
    attacker = TokenService(
        secret="9876543210abcdef9876543210abcdef", algorithm="HS256", access_ttl_minutes=15
    )  # знает токен, но не секрет

    with pytest.raises(pyjwt.InvalidTokenError):
        attacker.decode_access_token(token)


def test_access_token_ttl_seconds():
    assert make_service(access_ttl_minutes=15).access_token_ttl_seconds == 900


def test_refresh_tokens_are_unique_random_strings():
    first = TokenService.generate_refresh_token()
    second = TokenService.generate_refresh_token()

    assert first != second
