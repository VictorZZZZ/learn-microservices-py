"""add username to user_profile

Revision ID: 20261021_add_username
Revises: 20261020_create_profile_tables
Create Date: 2026-10-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20261021_add_username"
down_revision: Union[str, None] = "20261020_create_profile_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NOT NULL без server_default добавляется только в пустую таблицу:
    # существующим строкам было бы нечем заполнить колонку
    op.add_column(
        "user_profile",
        sa.Column("username", sa.String(255), nullable=False, unique=True),
    )


def downgrade() -> None:
    op.drop_column("user_profile", "username")
