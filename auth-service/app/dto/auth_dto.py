import uuid

from auth_contracts.role_name import RoleName
from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """Тело запроса на регистрацию."""

    username: str = Field(min_length=3, max_length=255)
    # bcrypt игнорирует всё после 72-го байта пароля, поэтому режем на входе
    password: str = Field(min_length=8, max_length=72)


class LoginRequest(BaseModel):
    """Тело запроса на логин."""

    username: str
    password: str


class RefreshRequest(BaseModel):
    """Тело запроса на обновление пары токенов."""

    refresh_token: str


class UserDto(BaseModel):
    """Ответ API: пользователь без пароля. id — UUID, в JSON уходит строкой."""

    id: uuid.UUID
    username: str
    enabled: bool
    roles: list[RoleName]


class TokenPairDto(BaseModel):
    """Пара токенов — ответ login/register/refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # время жизни access-токена в секундах


class RegisterResponseDto(BaseModel):
    """Ответ регистрации: созданный пользователь + сразу пара токенов."""

    user: UserDto
    tokens: TokenPairDto
