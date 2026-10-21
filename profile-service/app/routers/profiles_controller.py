from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_session
from app.dto.profile_dto import OrganizationProfileDto, UserProfileDto
from app.mappers.profile_mapper import to_organization_profile_dto, to_user_profile_dto
from app.repositories.organization_profile_repository import OrganizationProfileRepository
from app.repositories.user_profile_repository import UserProfileRepository
from app.security.dependencies import get_current_user
from app.security.principal import AuthenticatedUser

router = APIRouter(prefix="/v1", tags=["profiles"])


@router.get("/user-profile", response_model=UserProfileDto)
async def get_my_user_profile(
    session: AsyncSession = Depends(get_session),
    user: AuthenticatedUser = Depends(get_current_user),
) -> UserProfileDto:
    """Профиль того, кто сделал запрос.

    Чей профиль — решает JWT (claim uid), а не путь или параметр: свои данные
    может читать любой аутентифицированный пользователь, поэтому привилегия
    READ не нужна (ср. /v1/products в catalog-сервисе).
    """
    profile = await UserProfileRepository(session).find_by_user_id(user.user_id)
    if profile is None:
        # аккаунт есть в auth-сервисе, но профиль здесь ещё не заведён
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Профиль пользователя не найден")
    return to_user_profile_dto(profile)


@router.get("/org-profile", response_model=OrganizationProfileDto)
async def get_my_org_profile(
    session: AsyncSession = Depends(get_session),
    user: AuthenticatedUser = Depends(get_current_user),
) -> OrganizationProfileDto:
    """Организация текущего пользователя.

    organization_id в JWT нет (убрали оттуда), поэтому сначала находим
    профиль пользователя, а через него — организацию.
    """
    profile = await UserProfileRepository(session).find_by_user_id(user.user_id)
    if profile is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Профиль пользователя не найден")
    if profile.organization_id is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Пользователь не привязан к организации"
        )

    organization = await OrganizationProfileRepository(session).find_by_id(
        profile.organization_id
    )
    if organization is None:
        # при живом FK невозможно; страховка на случай, когда данные удалили мимо нас
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Организация не найдена")
    return to_organization_profile_dto(organization)
