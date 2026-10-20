"""Маппинг доменных ошибок AuthService в HTTP-ответы.

Аналог @RestControllerAdvice из Spring: контроллеры и сервисы кидают
доменные исключения, а здесь они превращаются в ответы с машиночитаемым
code и человекочитаемым message.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import (
    AccountDisabledError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UsernameAlreadyExistsError,
)


def _error(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует обработчики на переданном приложении (вызывается из main.py)."""

    @app.exception_handler(UsernameAlreadyExistsError)
    async def username_taken_handler(
        request: Request, exc: UsernameAlreadyExistsError
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content=_error("USERNAME_TAKEN", str(exc)))

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
        request: Request, exc: InvalidCredentialsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content=_error("INVALID_CREDENTIALS", "Неверный логин или пароль"),
        )

    @app.exception_handler(AccountDisabledError)
    async def account_disabled_handler(
        request: Request, exc: AccountDisabledError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=403, content=_error("ACCOUNT_DISABLED", "Аккаунт отключён")
        )

    @app.exception_handler(InvalidRefreshTokenError)
    async def invalid_refresh_token_handler(
        request: Request, exc: InvalidRefreshTokenError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content=_error(
                "INVALID_REFRESH_TOKEN", "Refresh-токен недействителен, истёк или отозван"
            ),
        )
