from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal


async def get_session() -> AsyncIterator[AsyncSession]:
    """Сессия на время HTTP-запроса (аналог EntityManager per request)."""
    async with SessionLocal() as session:
        yield session
