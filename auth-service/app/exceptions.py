class AuthError(Exception):
    """Базовый класс доменных ошибок auth-сервиса.

    Аналог своего BusinessException в Spring: сервис кидает доменную ошибку,
    а в main.py она превращается в HTTP-ответ (как @ControllerAdvice).
    """


class UsernameAlreadyExistsError(AuthError):
    def __init__(self, username: str) -> None:
        super().__init__(f"Username '{username}' is already taken")
        self.username = username


class InvalidCredentialsError(AuthError):
    """Неверный логин или пароль."""


class AccountDisabledError(AuthError):
    """Аккаунт отключён (users.enabled = false)."""


class InvalidRefreshTokenError(AuthError):
    """Refresh-токен не найден, отозван или истёк."""
