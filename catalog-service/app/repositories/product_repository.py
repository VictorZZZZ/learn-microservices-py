from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Product


class ProductRepository:
    """Инкапсулирует доступ к таблице product."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_all(self) -> list[Product]:
        stmt = select(Product).order_by(Product.id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, product_id: int) -> Product | None:
        stmt = select(Product).where(Product.id == product_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, product: Product) -> Product:
        self._session.add(product)
        await self._session.commit()
        # refresh перечитывает строку из базы: подтягивает id и created_at,
        # которые сгенерировала БД при INSERT
        await self._session.refresh(product)
        return product
