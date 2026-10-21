import os
from datetime import UTC, datetime, timedelta

# 32+ байта: PyJWT ругается на более короткие HMAC-ключи (RFC 7518)
TEST_SECRET = "0123456789abcdef0123456789abcdef"

# Дефолты для Settings, чтобы тесты не зависели от наличия .env.
# Ставим ДО импорта app.*: main.py при импорте читает настройки.
# setdefault не мешает локально — реальные env-переменные имеют приоритет.
os.environ.setdefault("DATABASE_HOST", "localhost")
os.environ.setdefault("DATABASE_USER", "postgres")
os.environ.setdefault("DATABASE_PASSWORD", "postgres")
os.environ.setdefault("DATABASE_NAME", "learn-py-profiles")
os.environ.setdefault("JWT_SECRET", TEST_SECRET)

import jwt as pyjwt  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db.dependencies import get_session  # noqa: E402
from app.main import app  # noqa: E402

USER_ID = "123e4567-e89b-12d3-a456-426614174000"


def make_access_token(
    roles: list[str],
    privileges: list[str],
    *,
    secret: str = TEST_SECRET,
    ttl_minutes: int = 15,
) -> str:
    """Собирает токен тем же способом, что TokenService auth-сервиса."""
    now = datetime.now(UTC)
    payload = {
        "sub": "jdoe",
        "uid": USER_ID,
        "roles": roles,
        "privileges": privileges,
        "iat": now,
        "exp": now + timedelta(minutes=ttl_minutes),
    }
    return pyjwt.encode(payload, secret, algorithm="HS256")


class _FakeResult:
    def __init__(self, rows: list) -> None:
        self._rows = rows

    def scalars(self) -> "_FakeResult":
        return self

    def all(self) -> list:
        return self._rows

    def scalar_one_or_none(self):
        return self._rows[0] if self._rows else None


class FakeSession:
    """Двойник AsyncSession без БД: хватает для SELECT-запросов репозиториев.

    execute() по очереди выдаёт заранее подготовленные группы строк — так тест
    задаёт, что вернёт первый запрос (профиль) и второй (организация).
    """

    def __init__(self, results: list[list] | None = None) -> None:
        self._results = list(results) if results else []

    async def execute(self, stmt) -> _FakeResult:
        rows = self._results.pop(0) if self._results else []
        return _FakeResult(rows)


def set_session_rows(*row_groups: list) -> None:
    """Подменяет сессию БД: каждый execute() вернёт следующую группу строк."""
    session = FakeSession(list(row_groups))

    async def override():
        yield session

    app.dependency_overrides[get_session] = override


@pytest.fixture
def client() -> TestClient:
    # подменяем только сессию с БД; безопасность (Bearer) работает по-настоящему
    set_session_rows()  # по умолчанию база «пустая»: любой SELECT ничего не вернёт
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_session, None)
