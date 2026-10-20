"""users: first_name/last_name become nullable

Revision ID: 20261019_names_nullable
Revises: 20261019_seed_roles
Create Date: 2026-10-19
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20261019_names_nullable"
down_revision: Union[str, None] = "20261019_seed_roles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("users", "first_name", existing_type=sa.String(255), nullable=True)
    op.alter_column("users", "last_name", existing_type=sa.String(255), nullable=True)


def downgrade() -> None:
    op.alter_column("users", "first_name", existing_type=sa.String(255), nullable=False)
    op.alter_column("users", "last_name", existing_type=sa.String(255), nullable=False)
