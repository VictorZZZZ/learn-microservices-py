"""create profile tables (organization_profile, user_profile)

Revision ID: 20261020_create_profile_tables
Revises:
Create Date: 2026-10-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20261020_create_profile_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organization_profile",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("unp", sa.String(9), nullable=True, unique=True),
        sa.Column("city", sa.String(255), nullable=True),
        sa.Column("address", sa.String(512), nullable=True),
        sa.Column("postal_code", sa.String(16), nullable=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("website", sa.String(512), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "is_test", sa.Boolean, nullable=False, server_default=sa.false()
        ),
    )
    op.create_table(
        "user_profile",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("first_name", sa.String(255), nullable=True),
        sa.Column("last_name", sa.String(255), nullable=True),
        sa.Column("position", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.String(512), nullable=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("telegram_id", sa.String(64), nullable=True),
        sa.Column(
            "organization_id",
            sa.Integer,
            sa.ForeignKey("organization_profile.id"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "is_test", sa.Boolean, nullable=False, server_default=sa.false()
        ),
    )
    op.create_index(
        op.f("ix_user_profile_organization_id"),
        "user_profile",
        ["organization_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_user_profile_organization_id"), table_name="user_profile"
    )
    op.drop_table("user_profile")
    op.drop_table("organization_profile")
