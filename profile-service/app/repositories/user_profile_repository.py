import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import UserProfile


class UserProfileRepository:
    """Инкапсулирует доступ к таблице user_profile."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_user_id(self, user_id: uuid.UUID) -> UserProfile | None:
        stmt = select(UserProfile).where(UserProfile.id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
