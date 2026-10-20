import uuid

from auth_contracts.privilege_name import PrivilegeName
from auth_contracts.role_name import RoleName

from app.db.models import Privilege, Role, User
from app.dto.auth_dto import RegisterRequest
from app.mappers.user_mapper import to_new_user, to_user_dto


def make_role(
    name: RoleName = RoleName.READ_ONLY, privileges: list[PrivilegeName] | None = None
) -> Role:
    return Role(name=name, privileges=[Privilege(name=p) for p in privileges or []])


def test_to_user_dto():
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        username="jdoe",
        password_hash="$2b$12$somehash",
        enabled=True,
        roles=[make_role(RoleName.READ_ONLY, [PrivilegeName.READ])],
    )

    dto = to_user_dto(user)

    assert dto.id == user_id
    assert dto.username == "jdoe"
    assert dto.enabled is True
    assert dto.roles == [RoleName.READ_ONLY]
    assert "password_hash" not in dto.model_dump()  # пароль не покидает сервис


def test_to_new_user():
    request = RegisterRequest(username="jdoe", password="s3cret-password")
    read_only = make_role()

    user = to_new_user(request, password_hash="$2b$12$somehash", roles=[read_only])

    assert user.id is None          # id сгенерируется при INSERT (default=uuid.uuid4)
    assert user.username == "jdoe"
    assert user.password_hash == "$2b$12$somehash"  # хеш, а не открытый пароль
    assert user.enabled is True     # новый пользователь сразу активен
    assert user.roles == [read_only]  # роль READ_ONLY из сид-миграции
