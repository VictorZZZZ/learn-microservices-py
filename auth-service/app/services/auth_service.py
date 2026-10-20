from datetime import UTC, datetime, timedelta

from auth_contracts.role_name import RoleName

from app.db.models import RefreshToken, User
from app.dto.auth_dto import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponseDto,
    TokenPairDto,
)
from app.exceptions import (
    AccountDisabledError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UsernameAlreadyExistsError,
)
from app.mappers.user_mapper import to_new_user, to_user_dto
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.services.password_service import hash_password, verify_password
from app.services.token_service import TokenService


class AuthService:
    """Сценарии регистрации и выдачи токенов (аналог @Service из Spring)."""

    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        token_service: TokenService,
        refresh_token_ttl_days: int,
    ) -> None:
        self._users = user_repository
        self._refresh_tokens = refresh_token_repository
        self._tokens = token_service
        self._refresh_token_ttl_days = refresh_token_ttl_days

    async def register(self, request: RegisterRequest) -> RegisterResponseDto:
        existing = await self._users.find_by_username(request.username)
        if existing is not None:
            raise UsernameAlreadyExistsError(request.username)

        # каждому новому пользователю — роль READ_ONLY (привилегия READ)
        read_only_role = await self._users.find_role_by_name(RoleName.READ_ONLY)
        if read_only_role is None:
            # сид-миграция не применена — это проблема сервера, а не клиента
            raise RuntimeError(
                "Роль READ_ONLY отсутствует в справочнике; выполни миграцию "
                "20261019_seed_roles"
            )

        user = to_new_user(request, hash_password(request.password), [read_only_role])
        saved = await self._users.save(user)
        tokens = await self._issue_tokens(saved)
        return RegisterResponseDto(user=to_user_dto(saved), tokens=tokens)

    async def login(self, request: LoginRequest) -> TokenPairDto:
        user = await self._users.find_by_username(request.username)
        # неизвестный логин и неверный пароль — один и тот же ответ,
        # чтобы не подсказывать, какие пользователи существуют
        if user is None or not verify_password(request.password, user.password_hash):
            raise InvalidCredentialsError()
        if not user.enabled:
            raise AccountDisabledError()
        return await self._issue_tokens(user)

    async def refresh(self, request: RefreshRequest) -> TokenPairDto:
        stored = await self._refresh_tokens.find_by_token(request.refresh_token)
        if stored is None or stored.revoked or stored.expires_at <= datetime.now(UTC):
            raise InvalidRefreshTokenError()
        user = stored.user
        if not user.enabled:
            raise AccountDisabledError()
        # ротация: старый refresh-токен отзываем, взамен выдаём новую пару
        await self._refresh_tokens.revoke(stored)
        return await self._issue_tokens(user)

    async def _issue_tokens(self, user: User) -> TokenPairDto:
        roles = [role.name for role in user.roles]
        # эффективные привилегии = привилегии ролей + прямые привилегии пользователя
        privileges = sorted(
            {privilege.name for role in user.roles for privilege in role.privileges}
            | {privilege.name for privilege in user.privileges}
        )
        access_token = self._tokens.create_access_token(
            user_id=user.id,
            username=user.username,
            roles=roles,
            privileges=privileges,
        )
        refresh_token = TokenService.generate_refresh_token()
        await self._refresh_tokens.save(
            RefreshToken(
                user_id=user.id,
                token=refresh_token,
                expires_at=datetime.now(UTC) + timedelta(days=self._refresh_token_ttl_days),
            )
        )
        return TokenPairDto(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._tokens.access_token_ttl_seconds,
        )
