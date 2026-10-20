from uuid import UUID

import jwt

from app.security.principal import AuthenticatedUser


class TokenVerifier:
    """Проверка access-токенов auth-сервиса (аналог JwtDecoder из Spring Security).

    Подпись HS256 симметричная, поэтому секрет общий у auth-сервиса и этого
    сервиса: токен, который подписал один, может проверить только владелец
    того же секрета. Права берём из claims — ходить в auth-сервис на каждый
    запрос не нужно.
    """

    def __init__(self, secret: str, algorithm: str) -> None:
        self._secret = secret
        self._algorithm = algorithm

    def verify(self, token: str) -> AuthenticatedUser:
        # decode проверяет подпись и срок действия; при проблемах — jwt.PyJWTError
        payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        try:
            return AuthenticatedUser(
                username=payload["sub"],
                user_id=UUID(payload["uid"]),
                roles=frozenset(payload["roles"]),
                privileges=frozenset(payload["privileges"]),
            )
        except (KeyError, ValueError) as e:
            # подпись верная, но обязательных claims нет или битые (uid не UUID) —
            # такой токен считаем недействительным
            raise jwt.InvalidTokenError(f"сломанные claims: {e}") from e
