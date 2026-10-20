from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.dependencies import get_session
from app.dto.auth_dto import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponseDto,
    TokenPairDto,
)
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.token_service import TokenService

router = APIRouter(prefix="/v1/auth", tags=["auth"])

settings = get_settings()

# у TokenService нет состояния (только настройки) — один экземпляр на приложение
token_service = TokenService(
    secret=settings.jwt_secret,
    algorithm=settings.jwt_algorithm,
    access_ttl_minutes=settings.access_token_ttl_minutes,
)


def build_auth_service(session: AsyncSession) -> AuthService:
    """Собирает зависимости вручную (DI без контейнера).

    Repository'ам нужна сессия текущего HTTP-запроса, поэтому граф
    пересобирается на каждый запрос — как request scope в Spring.
    """
    return AuthService(
        user_repository=UserRepository(session),
        refresh_token_repository=RefreshTokenRepository(session),
        token_service=token_service,
        refresh_token_ttl_days=settings.refresh_token_ttl_days,
    )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponseDto,
)
async def register(
    payload: RegisterRequest, session: AsyncSession = Depends(get_session)
) -> RegisterResponseDto:
    return await build_auth_service(session).register(payload)


@router.post("/login", response_model=TokenPairDto)
async def login(
    payload: LoginRequest, session: AsyncSession = Depends(get_session)
) -> TokenPairDto:
    return await build_auth_service(session).login(payload)


@router.post("/refresh", response_model=TokenPairDto)
async def refresh(
    payload: RefreshRequest, session: AsyncSession = Depends(get_session)
) -> TokenPairDto:
    return await build_auth_service(session).refresh(payload)
