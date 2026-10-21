from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import OrganizationProfile


class OrganizationProfileRepository:
    """Инкапсулирует доступ к таблице organization_profile."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, organization_id: int) -> OrganizationProfile | None:
        stmt = select(OrganizationProfile).where(
            OrganizationProfile.id == organization_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
