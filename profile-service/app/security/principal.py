from dataclasses import dataclass
from uuid import UUID

from auth_contracts.privilege_name import PrivilegeName
from auth_contracts.role_name import RoleName


@dataclass(frozen=True)
class AuthenticatedUser:
    """Кто именно сделал запрос (аналог UserDetails/Authentication из Spring Security).

    Роли и привилегии хранятся как frozenset[str]: токен может содержать
    значение, которого ещё нет в нашем enum (auth-сервис обновили раньше),
    и это не должно ломать разбор токена — просто проверка права не пройдёт.
    """

    username: str
    user_id: UUID
    roles: frozenset[str]
    privileges: frozenset[str]

    def has_role(self, role: RoleName) -> bool:
        return role.value in self.roles

    def has_privilege(self, privilege: PrivilegeName) -> bool:
        return privilege.value in self.privileges
