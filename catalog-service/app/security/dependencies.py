from auth_contracts.privilege_name import PrivilegeName
from auth_contracts.role_name import RoleName
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings
from app.security.principal import AuthenticatedUser
from app.security.token_verifier import TokenVerifier

# auto_error=False: с True FastAPI сам ответил бы 403 на отсутствующий токен,
# а по семантике HTTP это 401 Unauthorized; ошибку возвращаем сами
bearer_scheme = HTTPBearer(auto_error=False, description="Access-токен из auth-сервиса")


def get_token_verifier() -> TokenVerifier:
    settings = get_settings()
    return TokenVerifier(settings.jwt_secret, settings.jwt_algorithm)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    verifier: TokenVerifier = Depends(get_token_verifier),
) -> AuthenticatedUser:
    """Разбор заголовка Authorization: Bearer <token> (аналог фильтра Spring Security).

    Дефолтная защита роутера: подключается через Depends(get_current_user).
    """
    if credentials is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Требуется заголовок Authorization: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return verifier.verify(credentials.credentials)
    except jwt.PyJWTError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Токен недействителен или истёк",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_privilege(privilege: PrivilegeName):
    """Фабрика зависимостей: пускать только владельцев привилегии.

    Аналог @PreAuthorize("hasAuthority('READ')") — только не аннотация над
    методом, а аргумент с Depends(require_privilege(...)) в сигнатуре.
    """

    async def checker(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if not user.has_privilege(privilege):
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Нужна привилегия {privilege.value}")
        return user

    return checker


def require_role(role: RoleName):
    """Фабрика зависимостей: пускать только указанную роль (аналог hasRole(...))."""

    async def checker(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if not user.has_role(role):
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Нужна роль {role.value}")
        return user

    return checker
