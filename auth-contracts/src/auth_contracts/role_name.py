from enum import StrEnum


class RoleName(StrEnum):
    """Роли пользователей auth-домена.
    Единственный источник правды для значений ролей: сиды auth-сервиса и
    JWT-claim "roles" используют эти значения, потребители токена (например
    microservice_1) проверяют их этими же енумами.
    """

    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    READ_ONLY = "READ_ONLY"  # выдаётся каждому новому пользователю при регистрации
