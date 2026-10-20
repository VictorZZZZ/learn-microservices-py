"""seed roles and privileges

Revision ID: 20261019_seed_roles_and_privileges
Revises: 20261019_create_auth_tables
Create Date: 2026-10-19
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from auth_contracts.privilege_name import PrivilegeName
from auth_contracts.role_name import RoleName
from sqlalchemy import delete, insert, select

# revision identifiers, used by Alembic.
revision: str = "20261019_seed_roles"
down_revision: Union[str, None] = "20261019_create_auth_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# легковесные описания таблиц — чтобы миграция не зависела от ORM-моделей
roles_table = sa.table("roles", sa.column("id", sa.Integer), sa.column("name", sa.String))
privileges_table = sa.table(
    "privileges", sa.column("id", sa.Integer), sa.column("name", sa.String)
)
role_privileges_table = sa.table(
    "role_privileges", sa.column("role_id", sa.Integer), sa.column("privilege_id", sa.Integer)
)

# значения берём из пакета auth-contracts — это единственный источник правды,
# поэтому сиды в БД не разойдутся с JWT-claims (StrEnum — это str, SQLAlchemy
# спокойно кладёт его в varchar-колонку)
PRIVILEGES = [privilege.value for privilege in PrivilegeName]

# какие привилегии входят в каждую роль
ROLE_PRIVILEGES = {
    RoleName.ADMIN: [
        PrivilegeName.CREATE,
        PrivilegeName.UPDATE,
        PrivilegeName.DELETE,
        PrivilegeName.READ,
    ],
    RoleName.MANAGER: [PrivilegeName.CREATE, PrivilegeName.UPDATE, PrivilegeName.READ],
    RoleName.READ_ONLY: [PrivilegeName.READ],  # выдаётся каждому новому пользователю при регистрации
}


def upgrade() -> None:
    bind = op.get_bind()

    for name in PRIVILEGES:
        bind.execute(insert(privileges_table).values(name=name))

    for role_name, privilege_names in ROLE_PRIVILEGES.items():
        role_id = bind.execute(
            insert(roles_table).values(name=role_name).returning(roles_table.c.id)
        ).scalar_one()
        privilege_ids = bind.execute(
            select(privileges_table.c.id).where(privileges_table.c.name.in_(privilege_names))
        ).scalars().all()
        for privilege_id in privilege_ids:
            bind.execute(
                insert(role_privileges_table).values(role_id=role_id, privilege_id=privilege_id)
            )


def downgrade() -> None:
    # удалит только сидовые строки; если пользователи уже получили роли,
    # FK из user_roles не даст удалить роли (это ожидаемо)
    bind = op.get_bind()
    role_names = list(ROLE_PRIVILEGES)
    role_ids = bind.execute(
        select(roles_table.c.id).where(roles_table.c.name.in_(role_names))
    ).scalars().all()
    if role_ids:
        bind.execute(
            delete(role_privileges_table).where(role_privileges_table.c.role_id.in_(role_ids))
        )
    bind.execute(delete(roles_table).where(roles_table.c.name.in_(role_names)))
    bind.execute(delete(privileges_table).where(privileges_table.c.name.in_(PRIVILEGES)))
