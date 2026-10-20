from app.db.models import Role, User
from app.dto.auth_dto import RegisterRequest, UserDto


def to_new_user(request: RegisterRequest, password_hash: str, roles: list[Role]) -> User:
    """RegisterRequest -> новая сущность User (id присвоит БД при INSERT)."""
    return User(
        username=request.username,
        password_hash=password_hash,
        enabled=True,
        roles=roles,
    )


def to_user_dto(user: User) -> UserDto:
    """User -> UserDto: без пароля, роли достаём из загруженной связи."""
    return UserDto(
        id=user.id,
        username=user.username,
        enabled=user.enabled,
        roles=[role.name for role in user.roles],
    )
