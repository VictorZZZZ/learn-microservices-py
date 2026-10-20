"""users: drop first_name, last_name, org_id

Revision ID: 20261020_drop_user_names_org
Revises: 20261019_names_nullable
Create Date: 2026-10-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20261020_drop_user_names_org"
down_revision: Union[str, None] = "20261019_names_nullable"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("users", "first_name")
    op.drop_column("users", "last_name")
    op.drop_column("users", "org_id")


def downgrade() -> None:
    # first_name/last_name возвращаем nullable (как после 20261019_names_nullable).
    # org_id — с server_default: NOT NULL-колонку нельзя добавить в таблицу,
    # где уже есть строки, не дав значения для существующих.
    op.add_column("users", sa.Column("first_name", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(255), nullable=True))
    op.add_column(
        "users", sa.Column("org_id", sa.Integer(), nullable=False, server_default="0")
    )
