"""create product table

Revision ID: 20261017_create_product_table
Revises:
Create Date: 2026-10-17
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20261017_create_product_table"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "product",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("vehicle_type", sa.String(64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("product")
