from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RefreshToken


class RefreshTokenRepository:
    """Инкапсулирует доступ к таблице refresh_tokens."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, refresh_token: RefreshToken) -> RefreshToken:
        self._session.add(refresh_token)
        await self._session.commit()
        return refresh_token

    async def find_by_token(self, token: str) -> RefreshToken | None:
        # user (а с ним его роли) подгрузится автоматически: lazy="selectin"
        stmt = select(RefreshToken).where(RefreshToken.token == token)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke(self, refresh_token: RefreshToken) -> None:
        refresh_token.revoked = True
        await self._session.commit()
