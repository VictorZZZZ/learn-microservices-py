"""seed 5 products

Revision ID: 20261017_insert_test_data
Revises: 20261017_create_product_table
Create Date: 2026-10-17
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20261017_insert_test_data"
down_revision: Union[str, None] = "20261017_create_product_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# лёгкое описание таблицы: только колонки, которые нужны для вставки
product_table = sa.table(
    "product",
    sa.column("id", sa.BigInteger),
    sa.column("name", sa.String),
    sa.column("description", sa.Text),
    sa.column("vehicle_type", sa.String),
)

CARS = [
    {"id": 1, "name": "Audi A4", "description": "Business-class sedan with quattro AWD", "vehicle_type": "sedan"},
    {"id": 2, "name": "Volkswagen Golf", "description": "Compact and practical city hatchback", "vehicle_type": "hatchback"},
    {"id": 3, "name": "Skoda Octavia Combi", "description": "Spacious family wagon with a huge trunk", "vehicle_type": "universal"},
    {"id": 4, "name": "Toyota Corolla", "description": "Reliable best-selling sedan", "vehicle_type": "sedan"},
    {"id": 5, "name": "MINI Cooper", "description": "Iconic stylish hatchback", "vehicle_type": "hatchback"},
]


def upgrade() -> None:
    # created_at не указываем — сработает server_default now() из миграции 0001
    op.bulk_insert(product_table, CARS)

    # BIGSERIAL-последовательность не сдвигается, когда вставляем явные id;
    # без setval следующий INSERT из приложения взял бы id=1 и упал в конфликт
    op.execute("SELECT setval('product_id_seq', (SELECT MAX(id) FROM product))")


def downgrade() -> None:
    op.execute("DELETE FROM product WHERE id IN (1, 2, 3, 4, 5)")
