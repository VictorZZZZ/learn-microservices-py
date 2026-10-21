import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OrganizationProfile(Base):
    """Сущность organization_profile — ORM-отображение таблицы (аналог JPA @Entity)."""

    __tablename__ = "organization_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # УНП — учётный номер плательщика, 9 цифр; двух организаций с одним УНП не бывает
    unp: Mapped[str | None] = mapped_column(String(9), unique=True)
    city: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(String(512))
    postal_code: Mapped[str | None] = mapped_column(String(16))
    phone: Mapped[str | None] = mapped_column(String(32))
    website: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    # onupdate — SQLAlchemy сам подставляет now() в каждый UPDATE
    # (аналог @UpdateTimestamp из Hibernate; в БД триггера нет)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    is_test: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class UserProfile(Base):
    """Сущность user_profile — профиль пользователя (аналог JPA @Entity).

    Данные профиля вынесены сюда из auth-сервиса: auth отвечает за учётку
    (логин/пароль/роли), этот сервис — за «кто человек» и где работает.
    id совпадает с users.id auth-сервиса; FK между базами нет — у каждого
    микросервиса своя БД (database per service), связывает общий ключ в JWT.
    """

    __tablename__ = "user_profile"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    # копия username из auth-сервиса: базы у сервисов разные, джойнить не с чем —
    # дублируем, чтобы отдавать профиль без похода в auth
    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    first_name: Mapped[str | None] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    position: Mapped[str | None] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(String(512))
    phone: Mapped[str | None] = mapped_column(String(32))
    telegram_id: Mapped[str | None] = mapped_column(String(64))
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organization_profile.id"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    is_test: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
