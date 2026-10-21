from uuid import UUID

from pydantic import BaseModel


class UserProfileDto(BaseModel):
    """Ответ API: профиль текущего пользователя (без служебных полей)."""

    id: UUID
    username: str
    first_name: str | None
    last_name: str | None
    position: str | None
    avatar_url: str | None
    phone: str | None
    telegram_id: str | None
    organization_id: int | None


class OrganizationProfileDto(BaseModel):
    """Ответ API: организация (профиль организации) текущего пользователя."""

    id: int
    name: str
    unp: str | None
    city: str | None
    address: str | None
    postal_code: str | None
    phone: str | None
    website: str | None
