from datetime import datetime
import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Таблицы-связки many-to-many (аналог JPA @JoinTable).
# Описываем их отдельно и подключаем к сущностям через secondary.
user_role_table = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

user_privilege_table = Table(
    "user_privileges",
    Base.metadata,
    Column("user_id", Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("privilege_id", Integer, ForeignKey("privileges.id", ondelete="CASCADE"), primary_key=True),
)

role_privilege_table = Table(
    "role_privileges",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("privilege_id", Integer, ForeignKey("privileges.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    """Сущность users — ORM-отображение таблицы (аналог JPA @Entity)."""

    __tablename__ = "users"

    # UUID генерирует приложение (uuid4) — аналог UUID.randomUUID() в JPA.
    # БД тоже подстрахована server_default gen_random_uuid() в миграции.
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    # пароль в открытом виде не хранится никогда — только bcrypt-хеш
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # many-to-many через таблицу-связку (аналог @ManyToMany @JoinTable).
    # lazy="selectin" — подгружать роли отдельным SELECT'ом сразу при загрузке
    # пользователя: в async-SQLAlchemy ленивая загрузка «по требованию» не работает
    roles: Mapped[list["Role"]] = relationship(
        secondary=user_role_table, lazy="selectin"
    )
    # прямые привилегии, назначенные пользователю в обход ролей
    privileges: Mapped[list["Privilege"]] = relationship(
        secondary=user_privilege_table, lazy="selectin"
    )


class Role(Base):
    """Справочник ролей: ADMIN, MANAGER, READ_ONLY (заполняется сид-миграцией)."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    privileges: Mapped[list["Privilege"]] = relationship(
        secondary=role_privilege_table, lazy="selectin"
    )


class Privilege(Base):
    """Справочник привилегий: CREATE, UPDATE, DELETE, READ (сид-миграция)."""

    __tablename__ = "privileges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)


class RefreshToken(Base):
    """Выданный refresh-токен: случайная строка (не JWT), хранится в БД.

    Благодаря записи в БД можно делать ротацию (старый токен отзываем при
    выдаче нового) и отзывать все токены пользователя (logout).
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped[User] = relationship(lazy="selectin")
