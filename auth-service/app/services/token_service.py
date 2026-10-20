import secrets
import uuid
from datetime import UTC, datetime, timedelta

import jwt


class TokenService:
    """Создание и проверка токенов.

    Access-токен — JWT, подписанный по HS256 (аналог Jwts.builder() из jjwt).
    Refresh-токен — непрозрачная случайная строка: её валидность проверяется
    по таблице refresh_tokens, поэтому подписывать её не нужно.
    """

    def __init__(self, secret: str, algorithm: str, access_ttl_minutes: int) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._access_ttl_minutes = access_ttl_minutes

    @property
    def access_token_ttl_seconds(self) -> int:
        return self._access_ttl_minutes * 60

    def create_access_token(
        self,
        user_id: uuid.UUID,
        username: str,
        roles: list[str],
        privileges: list[str],
    ) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": username,  # standard claim: subject
            # payload JWT — это JSON, а JSON не умеет UUID; кладём строкой
            "uid": str(user_id),
            # роли и эффективные привилегии кладём в токен, чтобы другим
            # сервисам не приходилось ходить в auth-сервис за правами
            "roles": roles,
            "privileges": privileges,
            "iat": now,  # issued at
            "exp": now + timedelta(minutes=self._access_ttl_minutes),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> dict:
        """Проверяет подпись и срок действия; при проблемах кидает jwt.PyJWTError."""
        return jwt.decode(token, self._secret, algorithms=[self._algorithm])

    @staticmethod
    def generate_refresh_token() -> str:
        return secrets.token_urlsafe(64)
