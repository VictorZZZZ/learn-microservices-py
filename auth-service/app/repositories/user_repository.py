from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Role, User


class UserRepository:
    """Инкапсулирует доступ к таблице users (и связанным справочникам)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_role_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_username(self, username: str) -> User | None:
        # роли и привилегии подгрузятся автоматически: lazy="selectin" у модели
        stmt = select(User).where(User.username == username)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, user: User) -> User:
        self._session.add(user)
        await self._session.commit()
        # refresh перечитывает строку из базы: подтягивает id,
        # который сгенерировала БД при INSERT
        await self._session.refresh(user)
        return user
