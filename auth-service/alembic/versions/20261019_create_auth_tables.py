"""create auth tables

Revision ID: 20261019_create_auth_tables
Revises:
Create Date: 2026-10-19
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20261019_create_auth_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        # UUID-ключ: приложение генерирует uuid4, а server_default
        # gen_random_uuid() (PostgreSQL 13+) подстраховывает сырые SQL-вставки
        sa.Column(
            "id", sa.Uuid(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("username", sa.String(255), nullable=False, unique=True),
        sa.Column("first_name", sa.String(255), nullable=False),
        sa.Column("last_name", sa.String(255), nullable=False),
        sa.Column("org_id", sa.Integer, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.text("true")),
    )
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(64), nullable=False, unique=True),
    )
    op.create_table(
        "privileges",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(64), nullable=False, unique=True),
    )
    # таблицы-связки many-to-many: составной PK из двух FK
    op.create_table(
        "user_roles",
        sa.Column(
            "user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column(
            "role_id", sa.Integer, sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
        ),
    )
    op.create_table(
        "user_privileges",
        sa.Column(
            "user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column(
            "privilege_id",
            sa.Integer,
            sa.ForeignKey("privileges.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_table(
        "role_privileges",
        sa.Column(
            "role_id", sa.Integer, sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column(
            "privilege_id",
            sa.Integer,
            sa.ForeignKey("privileges.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("token", sa.String(128), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_table("role_privileges")
    op.drop_table("user_privileges")
    op.drop_table("user_roles")
    op.drop_table("privileges")
    op.drop_table("roles")
    op.drop_table("users")
